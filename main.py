import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11_ADAPTER
nonebot.init()
driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11_ADAPTER)
nonebot.load_plugins("plugins")
if __name__ == "__main__":
    nonebot.run(host="127.0.0.1", port=8080)
