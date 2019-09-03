"""
sample_insert.py
サンプルデータをデータベースに格納してみる
"""
import models
import db

if __name__ == '__main__':
    # サンプル質問
    question = models.Question('What\'s up?')
    db.session.add(question)
    db.session.commit()

    # サンプル選択肢
    choices = list()
    choice_1 = models.Choice(question.id, 'Fine.')
    choice_2 = models.Choice(question.id, 'Not bad')
    choice_3 = models.Choice(question.id, 'Bad...')

    choices.append(choice_1)
    choices.append(choice_2)
    choices.append(choice_3)

    db.session.add_all(choices)
    db.session.commit()

    # adminユーザを作成
    admin = models.User('admin', 'responder')
    db.session.add(admin)
    db.session.commit()

    db.session.close()
