# Personalized Hacker News feed
Create personal feed of stories from Hacker News using this [Telegram bot](https://t.me/HackerNews_personalized_bot).
Just add keywords, maybe set score threshold (default is 1) and the bot will send stories when any of these keywords are mentioned in the title of Hacker News thread. Keyword search implemented via case-insensitive containment test.

![Screenshot_25](https://user-images.githubusercontent.com/76647266/201554168-e98c4666-cf85-4968-8110-6554f85419ff.png)


## COMMANDS

```/add python, machine learning, _ai_```

Add keywords. Separate by comma.
To only match a whole word add underscore before and after desired keyword. Underscores will be replaced with whitespace, so '_ai_' will be equivalent to ' ai '.
Btw, this will match even if the keyword is the first or the last word of the title.
<br/><br/><br/>
```/set_score 100```

Filter out stories by score. Default is 1.
<br/><br/><br/>
```/keywords```

Lists your keywords.
<br/><br/><br/>
```/remove python, machine learning, _ai_```

Remove keywords. Separate by comma.
<br/><br/><br/>
```/help```

List all commands.
<br/><br/><br/>
```/stop```

Stop the bot. Erases your data.
