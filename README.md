<h1 align="center">HackerNews Alerts Bot</h1>
<h4 align="center">Telegram bot for all kinds of notifications from Hacker News</h4>

---

<h3 align="center"><a href="https://github.com/lawxls/HackerNews-personalized/tree/commands-2.0#commands">commands</a></h3>

---

Currently it can do:

- [Keyword alerts](https://github.com/lawxls/HackerNews-personalized/tree/commands-2.0#keyword-alerts)

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
