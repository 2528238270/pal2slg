"""
scripts文件夹下的所有文件应该由可视化编辑器生成，手动编辑有些繁琐
但目前本人还没有开发脚本可视化编辑器的想法，暂时先手动编辑吧。
"""
from . import talk

talk_script = {
    0: talk.part_1.test_script,
    1000: talk.npc_talk.npc1_1,
    1001: talk.npc_talk.npc1_2,
    2000: talk.part_1.story_test_script_0,
    2001: talk.part_1.story_test_script_1,
    2002: talk.part_1.story_test_script_2
}
