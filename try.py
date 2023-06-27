

text = "hey @roll 1d20+2 initiative nice"
slash_command = text.partition("@roll")[2].strip()
print "#slash_command="+slash_command+"#"
roll_syntax, _d, other_msg = slash_command.partition(' ')
print "#roll_syntax="+roll_syntax+"#"
print "#_d="+_d+"#"
print "#other_msg="+other_msg+"#"
