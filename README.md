# lenovo-sign
联想智选APP签到


## 使用
### 本地
  1. 安装依赖
  ```bash
  pip3 install requests toml
  ```
  2. 克隆本仓库
  ```bash
  git clone https://github.com/marigold233/lenovo-sign.git
  ```
  3. 在`config.toml`填入你的账号
  4. 完成！测试运行脚本

### 云函数
  
  **云函数的超时时间默认3秒设置大一点，比如30秒, 不改大会超时报错**
  1. 安装依赖
  ```bash
  cd src
  pip3 install requests toml --upgrade -t .
  ```
  2. 复制云函数版本目录的`lenovo_sign.py`代码复制到云函数里面的`index.py`, 创建`config.toml`文件，按照配置你的账号
  3. 完成！部署测试
  
  
## 更新
  - 2022.06.20  
  1. 优化本地版本  
  2. 支持云函数  
  - 2022.06.17  
  1. 支持类手机签到，送延保券。以前的版本不给。  
