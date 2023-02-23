<h1 align="center">HackerNews Alerts Bot</h1>

<p align="center">
  <a href="https://t.me/hackernews_alerts_bot"><img src="https://user-images.githubusercontent.com/76647266/207596416-8636a1aa-ccbb-4d9a-bcd6-ea7a22203c48.png" alt="Telegram-bot"></a>
</p>

<p align="center"><em>Telegram bot for all kinds of notifications from Hacker News</em></p>

<p align="center">
<a href="https://github.com/lawxls/HackerNews-personalized/actions" target="_blank">
    <img src="https://github.com/lawxls/HackerNews-personalized/workflows/Test/badge.svg" alt="Test">
</a>
<a href="https://results.pre-commit.ci/latest/github/lawxls/HackerNews-personalized/main" target="_blank">
    <img src="https://results.pre-commit.ci/badge/github/lawxls/HackerNews-personalized/main.svg" alt="pre-commit">
</a>
</p>

---

<p align="center"><a href="https://github.com/lawxls/HackerNews-Alerts-Bot#commands">commands</a></p>

---

Features:

- [Keyword alerts](https://github.com/lawxls/HackerNews-Alerts-Bot#keyword-alerts)

To-Do:
- Reply alerts
- Stories by domain name alerts
- New thread comments alerts

## Keyword alerts
Create personal feed of stories or monitor mentions of your brand, projects or topics you're interested in.

Keyword search implemented via case-insensitive containment test.

By default, if you don't specify options and just type ```/add python``` the bot will begin scanning both story titles & comment bodies

![Screenshot_11](https://user-images.githubusercontent.com/76647266/207441549-4617e1c9-bdb6-41f9-8e91-cd93ce7d025e.png)
![Screenshot_12](https://user-images.githubusercontent.com/76647266/207441488-cf3baad1-dc21-4a29-955a-48aed2f1a30f.png)

To create **personal feed of stories** add keywords with ```-stories``` option, E.g. ```/add python -stories```. With this option, the keyword will be checked only in story titles.

You can also use `/set_score` command with a specified score to filter out stories that do not pass set threshold. (Set to 1 by default)

## COMMANDS
- **Add keyword**

  ```/add KEYWORD [-whole-word, -stories, -comments]```

  Bot will scan both story titles & comment bodies if options are not specified.

  Options:

    - ```-whole-word```

      match whole word only

    - ```-stories```

      scan only thread titles

    - ```-comments```

      scan only comment bodies

  Examples:

    - ```/add project-name```

    - ```/add python -stories```

    - ```/add AI -whole-word -stories```

    - ```/add machine learning -stories```

<br/>

- **Set score threshold**

  ```/set_score SCORE```

  Filter out stories that do not pass set threshold. (Set to 1 by default).

<br/>

- **List keywords**

  ```/keywords```

<br/>

- **Remove keyword**

  ```/remove KEYWORD```

<br/>

- **Commands and general information**

  ```/help```

<br/>

- **Stop bot**

  ```/stop```

  Stop the bot and delete your data.
