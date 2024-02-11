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

- [Keyword monitoring](https://github.com/lawxls/HackerNews-Alerts-Bot#keyword-monitoring)
- [Follow users](https://github.com/lawxls/HackerNews-Alerts-Bot#follow-users)
- [Subscribe to a thread](https://github.com/lawxls/HackerNews-Alerts-Bot#subscribe-to-a-thread)
- [Stories by domain names](https://github.com/lawxls/HackerNews-Alerts-Bot#stories-by-domain-names)
- [Comment replies](https://github.com/lawxls/HackerNews-Alerts-Bot#comment-replies)

## Keyword Monitoring
Create a personal feed of stories or monitor mentions of your brand, projects, or topics you're interested in.

![Screenshot_11](https://user-images.githubusercontent.com/76647266/207441549-4617e1c9-bdb6-41f9-8e91-cd93ce7d025e.png)
![Screenshot_12](https://user-images.githubusercontent.com/76647266/207441488-cf3baad1-dc21-4a29-955a-48aed2f1a30f.png)

To set up monitoring of story titles and comment bodies, simply add a keyword via the ```/add``` command: ```/add python```

To monitor only story titles, use the ```-stories``` option: ```/add python -stories```

In addition, the `/set_score` command can be used to receive stories only if they meet a specified score threshold (set to 1 by default).

Keyword search is implemented via a case-insensitive containment test.

## Follow Users
Follow a user to get notified of new posts and/or comments.

Use the ```/follow``` command to receive notifications when a user posts a new story or comment: ```/follow hnuser123```

Use the ```-stories``` or ```-comments``` option to monitor only stories or comments: ```/follow hnuser123 -stories```

## Subscribe to a Thread
Receive an alert when a new comment appears in a thread.

![Screenshot_60](https://user-images.githubusercontent.com/76647266/221961215-95fa49f1-2d3f-4b2a-9cdd-7ddbc2cf1514.png)

Subscribe to a thread by ID: `/subscribe 34971530`

![Screenshot_62](https://user-images.githubusercontent.com/76647266/221963281-4c32d9c4-8847-411e-b7be-0a33c36071ea.png)

## Stories by Domain Names
Add domain names to receive alerts whenever new stories are submitted.

Add a domain name: `/watch example.com`

Stories are affected by the `/set_score` command.

## Comment Replies
Receive notifications when someone replies to one of your comments.

Add your username: `/notify hnuser123`

## COMMANDS

### Keyword Monitoring

- **Add a Keyword**

  ```/add KEYWORD [-whole-word, -stories, -comments]```

  If no options are specified, the bot will monitor both story titles and comments.

  Options:

    - ```-whole-word```
      to match the entire word

    - ```-stories```
      to monitor only thread titles

    - ```-comments```
      to monitor only comments

  Examples:

    - ```/add project-name```

    - ```/add python -stories```

    - ```/add AI -whole-word -stories```

    - ```/add machine learning -stories```

- **Set a Score Threshold**

  ```/set_score SCORE```

  Receive stories only if they meet a specified score threshold (set to 1 by default).

- **List Keywords**

  ```/keywords```

- **Remove a Keyword**

  ```/remove KEYWORD```

### Follow Users

- **Follow a User**

  ```/follow USERNAME [-stories, -comments]```

  If no options are specified, the bot will monitor new stories and comments.

  Options:

    - ```-stories```
      to monitor only new stories

    - ```-comments```
      to monitor only comments

  Examples:

    - ```/follow hnuser123```

    - ```/follow hnuser123 -stories```

- **List Followed Users**

  ```/followed_users```

- **Unfollow a User**

  ```/unfollow USERNAME```

### Subscribe to a Thread

- **Subscribe to a Thread**

  ```/subscribe ID```

- **List Subscriptions**

  ```/subscriptions```

- **Unsubscribe from a Thread**

  ```/unsubscribe ID```

### Stories by Domain Names

- **Follow a Domain Name**

  ```/watch DOMAIN NAME```

- **List Domain Names**

  ```/domains```

- **Unfollow a Domain Name**

  ```/abandon DOMAIN NAME```

### Comment Replies

- **Add a Username**

  ```/notify USERNAME```

- **Disable Notifications**

  ```/disable```

### General Commands

- **General Info**

  ```/help```

- **List of Commands**

  ```/commands```

- **Contacts**

  ```/contacts```

- **Stop the Bot and Delete Your Data**

  ```/stop```
