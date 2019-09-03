"""
urls.py
ルーティング用ファイル
"""
import responder

from auth import is_auth, authorized
import hashlib

from datetime import datetime, timedelta

from models import User, Question, Choice
import db

import matplotlib.pyplot as plt

api = responder.API(
    title='Polls Application with Responder',
    version='1.0',
    openapi='3.0.2',
    docs_route='/docs',
    description='This is a simple polls application referenced Django tutorials with Responder 1.3.1.',
    contact={
        'name': 'RightCode Inc. Support',
        'url': 'https://rightcode.co.jp/contact',
        'email': '****@abcdefg.com'
    }
)

# ModelSchemaをimport
import schemas


# staticをjinja2で解決するためにstaticフィルタを定義
def static_filter(path):
    return '/static/' + path


# staticをフィルタに追加
api.jinja_env.filters['static'] = static_filter

# グローバル変数に登録する場合
api.jinja_env.globals['static'] = '/static/'


@api.route('/')
class Index:
    """
    ---
    get:
        description: Get Question list except future questions
        responses:
           200:
               description: Success
    """
    def on_get(self, req, resp):

        # 最新5個の質問を降順で取得
        questions = self.get_queryset()

        # 最新かどうか
        emphasized = [question.was_published_recently() for question in questions]

        # フォーマットを変更して必要なものだけ
        pub_date = [q.pub_date.strftime('%Y-%m-%d %H:%M:%S') for q in questions]

        resp.content = api.template("index.html",
                                    questions=questions,
                                    emphasized=emphasized,
                                    pub_date=pub_date,
                                    )

    def get_queryset(self, latest=5):
        """
        最新latest個の質問を返す
        :param latest:
        :return:
        """
        # 公開日の大きいものでソートして取得
        # filter()で現在日時より小さいものを取得する
        questions = db.session.query(Question).\
            filter(Question.pub_date <= datetime.now()).order_by(Question.pub_date.desc()).all()

        db.session.close()

        return questions[:latest]


@api.route('/admin')
def admin(req, resp):
    resp.content = api.template("admin.html")


@api.route('/ad_login')
class AdLogin:
    """
    ---
    get:
        description: Redirect Login view (admin.html)
    post:
        description: If login successes, redirect admin page view (administrator.html).
        parameters:
            - name: username
              in: body
              required: true
              description: username
              schema:
                type: strings
                properties:
                    username:
                      type: string
                      example: hogehoge

            - name: password
              in: body
              required: true
              description: password
              schema:
                type: strings
                properties:
                    password:
                        type: string
                        example: a1B2c3D4e5
        responses:
           200:
               description: Redirect administrator page.

    """
    async def on_get(self, req, resp):  # getならリダイレクト
        resp.content = api.template('admin.html')

    async def on_post(self, req, resp):

        data = await req.media()
        error_messages = []

        if data.get('username') is None or data.get('password') is None:
            error_messages.append('ユーザ名またはパスワードが入力されていません。')
            resp.content = api.template('admin.html', error_messages=error_messages)
            return

        username = data.get('username')
        password = hashlib.md5(data.get('password').encode()).hexdigest()

        if not is_auth(username, password):
            # 認証失敗
            error_messages.append('ユーザ名かパスワードに誤りがあります。')
            resp.content = api.template('admin.html', error_messages=error_messages)
            return

        # 認証成功した場合cookieにユーザを追加しリダイレクト
        resp.set_cookie(key='username', value=username, expires=None, max_age=None)
        resp.session['username'] = username
        api.redirect(resp, '/admin_top')


@api.route('/admin_top')
async def on_session(req, resp):
    """
    管理者ページ
    """

    authorized(req, resp, api)

    # GETメソッドでフィルタを受け取る
    date_filter = None
    q_str = ''
    if 'filter' in req.params:
        date_filter = req.params['filter']

    ''' [追加] 検索文字列を取得 '''
    if 'q_str' in req.params:
        q_str = req.params['q_str']

    # ログインユーザ名を取得
    auth_user = req.cookies.get('username')

    # データベースから質問一覧と選択肢を全て取得
    ''' [修正] URLクエリがなければ全部取得 '''
    if date_filter is None and (q_str is None or q_str == ''):
        questions = db.session.query(Question).all()
    # URLクエリがあればフィルタをかけて取得
    else:
        ''' [修正] 各URLクエリの組み合わせによって処理を変える '''
        if date_filter is not None:
            today = datetime.now()
            # 時間はいらない
            date_range = datetime(today.year, today.month, today.day) - timedelta(days=int(date_filter))

            if q_str is None and q_str == '':  # 投稿日検索のみ
                questions = db.session.query(Question).filter(Question.pub_date >= date_range).all()

            else:  # 両方
                questions = db.session.query(Question).\
                    filter(Question.pub_date >= date_range, Question.question_text.like('%'+q_str+'%')).all()

        else:  # 文字列検索のみ
            # LIKEで取得
            questions = db.session.query(Question).filter(Question.question_text.like('%'+q_str+'%')).all()
        
    choices = db.session.query(Choice).all()
    db.session.close()

    # 直近の投稿か否か
    was_recently = [q.was_published_recently() for q in questions]

    # 各データを管理者ページに渡す
    resp.content = api.template('administrator.html',
                                auth_user=auth_user,
                                questions=questions,
                                choices=choices,
                                was_recently=was_recently,
                                )


@api.route('/logout')
async def logout(req, resp):
    # クッキーとセッションを削除
    resp.set_cookie(key='username', value='', expires=0, max_age=0)
    resp.session.pop('username')
    api.redirect(resp, '/admin')


@api.route('/add_Question')
class AddQuestion:
    async def on_get(self, req, resp):
        """
        getの場合は追加専用ページを表示させる。
        """
        authorized(req, resp, api)
        date = datetime.now()

        resp.content = api.template('add_question.html', date=date)

    async def on_post(self, req, resp):
        """
        postの場合は受け取ったデータをQuestionテーブルに追加する。
        """
        data = await req.media()
        error_messages = list()

        """ エラー処理 """
        if data.get('question_text') is None:
            error_messages.append('質問内容が入力されていません。')

        if data.get('date') is None or data.get('time') is None:
            error_messages.append('公開日時が入力されていません。')

        # 配列として受け取ったフォームはget_list()で取得する
        choices = data.get_list('choices[]')
        votes = data.get_list('votes[]')

        if len(choices) == 0 or len(votes) == 0 or len(choices) != len(votes):
            error_messages.append('選択肢内容に入力されていない項目があります。')

        if len(choices) < 1:
            error_messages.append('選択肢は2つ以上必要です。')

        # 何かしらエラーがあればリダイレクト
        if len(error_messages) != 0:
            resp.content = api.template('add_question.html', error_messages=error_messages, date=datetime.now())
            return

        """ テーブルにQuestionを追加 """
        # 公開日時をセパレートしてint型のリストに変換
        date = [int(d) for d in data.get('date').split('-')]
        time = [int(t) for t in data.get('time').split(':')]

        # question作成
        question = Question(data.get('question_text'),
                            datetime(date[0], date[1], date[2],
                                     time[0], time[1], time[2]))
        # question追加
        db.session.add(question)
        db.session.commit()

        """ テーブルにChoicesを追加 """
        # まず外部キーとなるQuestion.idを取得
        foreign_key = question.id
        q_choices = list()

        for i, choice in enumerate(choices):
            # choice作成
            q_choices.append(
                Choice(foreign_key, choice, int(votes[i]))
            )

        # choice追加
        db.session.add_all(q_choices)
        db.session.commit()

        db.session.close()

        api.redirect(resp, '/admin_top')


@api.route('/add_Choice')
class AddChoice:
    async def on_get(self, req, resp):
        """
        getの場合は追加専用ページを表示させる。
        """
        authorized(req, resp, api)

        questions = db.session.query(Question.id, Question.question_text)
        db.session.close()

        resp.content = api.template('add_choice.html', questions=questions)

    async def on_post(self, req, resp):
        """
        postの場合は受け取ったデータをQuestionテーブルに追加する。
        """
        data = await req.media()
        error_messages = list()

        # もし何も入力されていない場合
        if data.get('choice_text') is None:
            error_messages.append('選択肢が入力されていません。')
            questions = db.session.query(Question.id, Question.question_text)
            resp.content = api.template('add_choice.html', error_messages=error_messages, questions=questions)
            return

        # テーブルに追加
        choice = Choice(data.get('question'), data.get('choice_text'))
        db.session.add(choice)
        db.session.commit()
        db.session.close()

        api.redirect(resp, '/admin_top')


@api.route('/change/{table_name}/{data_id}')
class ChangeData:
    async def on_get(self, req, resp, table_name, data_id):
        authorized(req, resp, api)

        table = Question if table_name == 'question' else Choice
        # [table].id == data_idとなるようなレコードをひとつ持ってくる
        field = db.session.query(table).filter(table.id == data_id).first()
        db.session.close()

        resp.content = api.template('/change.html', field=field, table_name=table_name)

    async def on_post(self, req, resp, table_name, data_id):
        data = await req.media()
        error_messages = list()

        # もし何も入力されていない場合
        text = table_name + '_text'
        if data.get(text) is None:
            error_messages.append('フィールドに入力されていない項目があります。')
            resp.content = api.template('change.html', error_messages=error_messages,
                                        field=data, table_name=table_name)
            return

        # データを更新
        table = Question if table_name == 'question' else Choice
        record = db.session.query(table).filter(table.id == data_id).first()

        if table is Question:
            record.question_text = data.get(text)
            record.pub_date = datetime(
                int(data['year']),
                int(data['month']),
                int(data['day']),
                int(data['hour']),
                int(data['minute']),
                int(data['second'])
            )
        else:
            record.choice_text = data.get(text)

        db.session.commit()
        db.session.close()

        api.redirect(resp, '/admin_top')


@api.route('/delete/{table_name}/{data_id}')
class DeleteData:
    async def on_get(self, req, resp, table_name, data_id):
        authorized(req, resp, api)

        table = Question if table_name == 'question' else Choice
        # table.id == data_idとなるようなレコードをひとつ持ってくる
        field = db.session.query(table).filter(table.id == data_id).first()
        resp.content = api.template('/delete.html', field=field, table_name=table_name)

    async def on_post(self, req, resp, table_name, data_id):

        # データを削除
        table = Question if table_name == 'question' else Choice
        record = db.session.query(table).filter(table.id == data_id).first()
        db.session.delete(record)

        # 紐づいた質問も削除
        if table is Question:
            choices = db.session.query(Choice).filter(Choice.question == data_id).all()
            for choice in choices:
                db.session.delete(choice)

        db.session.commit()
        db.session.close()

        api.redirect(resp, '/admin_top')


@api.route('/detail/{q_id}')
class Detail:
    async def on_get(self, req, resp, q_id):
        db.session.close()

        question = db.session.query(Question).filter(Question.id == q_id).first()
        choices = db.session.query(Choice).filter(Choice.question == q_id).all()
        db.session.close()

        # 公開日前の日付なら404リダイレクト
        if question.pub_date > datetime.now():
            resp.content = self.template('404.html')

        resp.content = api.template('/detail.html', question=question, choices=choices)


@api.route('/vote/{q_id}')
class Vote:
    async def on_post(self, req, resp, q_id):
        # postデータを取得
        data = await req.media()

        # 該当するchoiceを取得しvoteをインクリメント
        choice = db.session.query(Choice).filter(Choice.id == data.get('choice')).first()
        choice.votes += 1
        db.session.commit()

        db.session.close()

        # リダイレクト
        url_redirect = '/result/' + str(q_id)
        api.redirect(resp, url_redirect)


@api.route('/result/{q_id}')
class Result:
    async def on_get(self, req, resp, q_id):
        question = db.session.query(Question).filter(Question.id == q_id).first()
        choices = db.session.query(Choice).filter(Choice.question == q_id).all()

        db.session.close()

        # ファイルの保存先とファイル名
        file = 'static/images/q_' + str(question.id)

        choice_text_list = [choice.choice_text for choice in choices]
        choice_vote_list = [int(choice.votes) for choice in choices]

        sum_votes = sum(choice_vote_list)
        vote_rates = [float(vote / sum_votes) for vote in choice_vote_list]

        # タイトルと棒グラフ描画
        plt.title(question.question_text + ' (Total ' + str(sum_votes) + ' votes)')
        plt.bar(choice_text_list, choice_vote_list, color='skyblue')

        # 割合と投票人数を表示する
        # 有効桁数は小数点第１位までにする。
        for x, y, v in zip(choice_text_list, vote_rates, choice_vote_list):
            plt.text(x, v, str(v)+' votes\n' + str(round(y*100, 1))+'%', ha='center', va='bottom')

        # テキストが被らないように、y軸上限は常に最大投票数の1.2倍にしておく
        plt.ylim(0, round(max(choice_vote_list)*1.2))

        plt.savefig(file + '.svg', format='svg')
        plt.close()

        # matplotlibによって保存されたsvgファイルはHTMLで展開する際、冒頭4行はいらない (注: あまりよくないコーディング)
        # いるのは<svg>タグ内のみ
        svg = open(file + '.svg', 'r').readlines()[4:]

        resp.content = api.template('result.html', question=question, choices=choices, svg=svg)

