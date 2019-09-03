"""
test_question.py
サンプルテストケース
"""
import pytest
import run as myApp

from datetime import datetime, timedelta

from models import Question


@pytest.fixture
def api():
    return myApp.api


class TestQuestionModel:
    def test_was_published_recently_with_future_question(self, api):
        """
        未来の質問に対してwas_published_recently()はFalseを返すはずである
        :param api:
        :return:
        """
        # 未来の公開日となる質問を作成
        time = datetime.now() + timedelta(days=30)
        feature_question = Question('future_question', pub_date=time)

        # これはFalseとなるはず
        assert feature_question.was_published_recently() is False

    def test_was_published_recently_with_boundary_question(self, api):
        """
        == 境界値テスト ==
        １日１秒前の質問に対してはwas_published_recently()はFalseを返すはずである
        また，23時間59分59秒以内であればwas_published_recently()はTrueを返すはずである
        :param api:
        :return:
        """
        # 最近の境界値となる質問を作成
        time_old = datetime.now() - timedelta(days=1)
        time_res = datetime.now() - timedelta(hours=23, minutes=59, seconds=59)
        old_question = Question('old_question', time_old)
        res_question = Question('resent_question', time_res)

        assert old_question.was_published_recently() is False
        assert res_question.was_published_recently() is True


