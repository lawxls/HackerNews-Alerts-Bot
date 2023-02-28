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
- [Subscribe to a thread](https://github.com/lawxls/HackerNews-Alerts-Bot#subscribe-to-a-thread)

To-Do:
- Reply alerts
- Stories by domain name alerts

## Keyword alerts
Create personal feed of stories or monitor mentions of your brand, projects or topics you're interested in.

![Screenshot_11](https://user-images.githubusercontent.com/76647266/207441549-4617e1c9-bdb6-41f9-8e91-cd93ce7d025e.png)
![Screenshot_12](https://user-images.githubusercontent.com/76647266/207441488-cf3baad1-dc21-4a29-955a-48aed2f1a30f.png)

To set up monitoring of story titles and comment bodies, simply add keyword via ```/add``` command: ```/add python```

To monitor story titles only, use ```-stories``` option: ```/add python -stories```

In addition, the `/set_score` command can be used to receive stories only if they meet a specified score threshold (set to 1 by default).

Keyword search implemented via case-insensitive containment test.

## Subscribe to a thread
Monitor new comments of a thread.

![Screenshot_60](https://user-images.githubusercontent.com/76647266/221961215-95fa49f1-2d3f-4b2a-9cdd-7ddbc2cf1514.png)

Subscribe to a thread by id: `/subscribe 34971530`

![Screenshot_62](https://user-images.githubusercontent.com/76647266/221963281-4c32d9c4-8847-411e-b7be-0a33c36071ea.png)

## COMMANDS

### Keyword alerts commands

<br/>

- **Add keyword**

  ```/add KEYWORD [-whole-word, -stories, -comments]```

  If no options are specified, the bot will monitor both story titles and comment bodies.

  Options:

    - ```-whole-word```

      match whole word

    - ```-stories```

      only monitor thread titles

    - ```-comments```

      only monitor comment bodies

  Examples:

    - ```/add project-name```

    - ```/add python -stories```

    - ```/add AI -whole-word -stories```

    - ```/add machine learning -stories```

<br/>

- **Set score threshold**

  ```/set_score SCORE```

  Receive stories only if they meet a specified score threshold (set to 1 by default).

<br/>

- **List keywords**

  ```/keywords```

<br/>

- **Remove keyword**

  ```/remove KEYWORD```

<br/>

### Subscribe to a thread commands

<br/>

- **Subscribe to a thread**

  ```/subscribe ID```

<br/>

- **List subscriptions**

  ```/subscriptions```

<br/>

- **Unsubscribe from a thread**

  ```/unsubscribe ID```

<br/>

### General commands

<br/>

- **Commands and other info**

  ```/help```

<br/>

- **Stop the bot and delete your data**

  ```/stop```
