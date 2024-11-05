# 六人猫狗行：安全云盘网站


> 进阶团队实践训练：基于 Python 语言的 Flask 框架搭建的 Web 应用服务场景

```shell
│  README.md
│
├─breakIt
│  │  check.py
│  │  EXP.py
│  └─ README.md # Write-Up
│
├─buildIt
│  │  README.md # 软件文档
│  │
│  ├─docker
│  │      docker-compose.yml
│  │      Dockerfile
│  │      README.md # Docker 部署说明
│  │
│  └─source
│      │  app.py
│      │  ...
│      │  flag.txt
│      │  Pipfile
│      │  Pipfile.lock
│      │  README.md # 源码编译说明
│      └─ ... # 详见软件文档说明
│
├─fixIt
│  │  fixit.patch
│  └─ README.md # 补丁说明
│
└─report
    ├─ XXX # 个人实践报告
    │      README.md
    └─ ...
```


## 团队分工

- *buildIt*
  - **Docker** 宋奕萱
  - [source 基础代码](https://gitee.com/long-yunxi/cainiao-e-station) 兰芷萱 宋奕萱 杨欣悦
    - **source 二次开发** 时卉 兰芷萱 宋奕萱
- *breakIt*
  - **EXP** 李怡乐 晏梓莘
  - **checker** 李怡乐
- *fixIt*  晏梓莘
- *Vulnerability Design*
  - **SSTI** 杨欣悦
  - **Flask Session 伪造** 晏梓莘 李怡乐
  - **反序列化漏洞** 时卉


## 视频演示

> **改进**：根据口头报告后老师的建议，增加了 `EXP.py` 的日志输出

- [【1】Docker 部署](https://www.bilibili.com/video/BV1TDbie2Enj/) 
- [【2】攻击者流程](https://www.bilibili.com/video/BV12Dbie1EYi/) 
- [【3】EXP 自动化](https://www.bilibili.com/video/BV12Dbie1Esz/) 
- [【4】patch 修复](https://www.bilibili.com/video/BV12Dbie1EYi/) 


## :cat: 背景 :dog:

你是「中传放心传」云盘网站的一名普通用户，常年困扰于此网站对于普通用户的文件上传限制，对管理员用户的权限欣羡不已！于是你找到了网站的搭建者（有猫有狗？！），这是一群普通的学生，她们这样说道：

-  想要的话可以全部给你，去找吧！我把 **flag** 放在那里。
  
这些猫猫狗狗在网站里添加了一些小小的提示！只要你找到 flag，她们就答应让你加入成为「中传放心传」的尊贵会员之一，扩大上传权限，走上人生巅峰！<del>虽然可能没有多大用处。</del>