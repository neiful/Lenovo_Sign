# lenovo-sign


## 本地使用
  1. 安装依赖
  ```bash
  pip3 install requests toml jsonpath
  ```
  2. 克隆本仓库
  ```bash
  git clone https://github.com/marigold233/lenovo-sign.git
  ```
  3. 在`config.toml`填入你的账号和选择推送通知的类型，也可以不选择推送，不填即可
  4. 测试运行脚本
  ```bash
  python3 lenovo_sign.py
  ```
  5. 加入crontab计划任务
  ```bash
  # 查看python3解释器绝对路径，crontab里面要写解释器绝对路径
  which python3
  /usr/local/bin/python3
  # 每天上午九点运行
  0 9 * * * /usr/local/bin/python3 lenovo_sign.py &> lenovo_sign.log
  ``` 

## 云函数使用
  **云函数的超时时间默认3秒设置大一点，比如30秒, 不改大会超时报错**
  1. 安装依赖
  ```bash
  cd src
  pip3 install requests toml jsonpath --upgrade -t .
  ```
  2. 复制云函数版本目录的`lenovo_sign.py`代码到云函数里面的`index.py`，复制`message_push.py`和`config.toml`到云函数， 
  在`config.toml`按照配置你的账号和选择推送通知的类型，也可以不选择推送，不填即可
  3. 完成！部署测试

## 青龙面板使用
1. 安装python依赖`requests toml jsonpath`
2. 把文件`lenovo_sign.py`、`message_push.py`、`config.toml`上传到青龙面板，然后按要求配置账号和提送类型即可，也可以不选择推送，不填即可。

## 支持推送消息类型
- server酱
- 企业微信应用
  
## 更新
  - 2022.08.16
  1. 添加签到消息推送
  - 2022.08.07
  1. 修复签到不给延保的问题  
  - 2022.06.20  
  1. 优化本地版本  
  2. 支持云函数  
  - 2022.06.17  
  1. 支持类手机签到，送延保券。以前的版本不给。  
