# coding=utf-8
from workflow import Workflow3, ICON_WEB
import sys
import os
import argparse

log = None
reload(sys)
sys.setdefaultencoding('utf8')


KEEP_ICON = os.path.dirname(os.path.abspath(__file__)) + '/icon.icns'


def is_ascii(s):
    return all(ord(c) < 128 for c in s)


def to_ascii(s):
    ulabel = s.decode("utf-8")
    if not is_ascii(ulabel):
        return s
    return ulabel.encode("ascii", "ignore")


def get_notes(query):
    import gkeepapi
    import json

    keep = gkeepapi.Keep()

    if query == u'#':
        return None
    log.info("正在查询文件...")
    # Load cache
    fh = open('state', 'r')
    state = json.load(fh)
    keep.restore(state)

    gnotes = []

    # 默认查询固定笔记
    if not query:
        notes = keep.find(pinned=True)
    # 以#开头时按标签查询
    elif query.startswith('#'):
        notes = keep.find(labels=[keep.findLabel(to_ascii(query[1:]))])
    # 按关键词查询
    else:
        notes = keep.find(query=query)

    result = []
    for note in notes:
        result.append(note)

    if len(result) < 1:
        return None
    return result


def main(wf):
    parser = argparse.ArgumentParser()

    parser.add_argument('query', nargs='?', default=None)
    args = parser.parse_args(wf.args)
    query = args.query

    def cacheable_notes():
        return get_notes(query)

    notes = wf.cached_data(query, cacheable_notes, max_age=3600*24)

    if notes is None:
        wf.add_item(title='没有找到结果',  subtitle='请输入标签', icon=KEEP_ICON)
        wf.send_feedback()
        return 0

    for note in notes:
        tags = [x.name for x in note.labels.all()]
        tag = ''
        if len(tags):
            tag = '['+']['.join(tags)+']'
        wf.add_item(
            title=note.title,
            subtitle=note.text,
            largetext=note.text,
            quicklookurl="http://www.deanishe.net/alfred-workflow",
            arg='$$'.join([note.title, note.text,  tag,
                           "https://keep.google.com/#NOTE/" + note.server_id]),
            uid=note.server_id, valid=True, icon=KEEP_ICON)

    if len(wf._items) < 1:
        wf.add_item(title='没有找到结果',  subtitle='请重新搜索', icon=KEEP_ICON)

    wf.send_feedback()


if __name__ == '__main__':
    wf = Workflow3(libraries=['./libs'])
    log = wf.logger
    sys.exit(wf.run(main))
