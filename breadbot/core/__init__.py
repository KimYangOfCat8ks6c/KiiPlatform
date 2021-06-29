import random
import re
from pymongo import MongoClient

from . import data
from . import dia
from . import klg
from . import memory
from . import misc
from . import search
from . import teach


class chat(object):

    def __init__(self):
        self.db = self._open_db()

    def _open_db(self):
        db_name = misc.cfg().get('db_name')
        db_ip = misc.cfg().get('db_ip')
        db_port = misc.cfg().get('db_port')
        client = MongoClient(db_ip, db_port)
        return client[db_name]

    def response(self, user, inStr):
        inStr = misc.init_input(inStr)
        res = ''

        if re.match('^n$', inStr):
            res = memory.longStr(user).read_mem()

        if misc.is_super(user):
            if re.match('^d .*$', inStr):
                content = re.sub('^d ', '', inStr)
                res = search.translate(content)
            elif re.match('^s .*$', inStr):
                content = re.sub('^s ', '', inStr)
                res = klg.response(self.db, user, content)
                if not res:
                    res = search.baiduSearch(content)
            elif re.match('^w .*$', inStr):
                content = re.sub('^w ', '', inStr)
                res = search.wikiSearch(content)
            elif re.match('^help$', inStr.lower()):
                res = misc.show_help()
            elif re.match('^readme$', inStr.lower()):
                res = misc.show_readme()
            elif re.match('^t .*$', inStr):
                content = re.sub('^t ', '', inStr)
                res = teach.response(user, content)
            elif re.search('[\u4e00-\u9fa5]', inStr):
                res = search.baiduSearch(inStr)
        else:
            if re.search('[\u4e00-\u9fa5]', inStr):
                resList = [
                    'I speak English only.',
                    'Speak English please.',
                    'English, please.']
                return random.choice(resList)
        if not res:
            lastDias = memory.dialogue(user).get_dia()
            if lastDias:
                lastDia = lastDias[-1]
                que = list(lastDia.keys())[0]
                ans = list(lastDia.values())[0]
            if inStr == que or klg.DO_YOU_MEAN in ans:
                res = klg.response(self.db, user, inStr)
                if not res:
                    res = dia.response(self.db, user, inStr)
            else:
                res = dia.response(self.db, user, inStr)
        if not res:
            notList = [
                "I don't understand",
                "What?",
                "Let's change a topic",
                "I don't know",
                "Parden?",
                "Hmm..."]
            res = random.choice(notList)
        memory.dialogue(user).insert_dia(inStr, res)
        res = memory.longStr(user).check_long_str(res)
        return res
