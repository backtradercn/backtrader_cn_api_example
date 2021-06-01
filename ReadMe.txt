免费提供基于backtrader的中国期货ctp行情以及交易接口。

https://blog.csdn.net/BackTraderCN/article/details/117473909
https://github.com/backtradercn/backtrader_cn_api_example

本安装包默认包含window和Linux版的ctp行情以及交易功能。

# backtrader-cn 接口，已经接入了高频系统(参考课程 https://edu.csdn.net/course/detail/24668) 的md/td模块，可以直接使用ctp，飞马，xtp，及一些非法币交易所。默认安装包仅提供ctp接入，其他安装包请联系课程主管。
# 行情以及交易接口已经改造为power-save模式，通过增加延迟减少cpu耗费。如需原始高频模式，请联系课程主管。
# 内置接口已经可以直接读取收集中国期货ctp的tick数据和分钟线（参考期货tick自动下载和分钟线处理环境 https://blog.csdn.net/BackTraderCN/article/details/116597823）


免责声明：详见《RISK_DISCLOSURE_AGREEMENT.txt》



#安装
#win


python -m easy_install backtradercn-1.0-py3.7-win-amd64.egg
cd c:\anaconda3\lib\site-packages\backtradercn-1.0-py3.7-win-amd64.egg
c:
copy pystrategy.pyd  backtradercn\

#linux 

mkdir /home/bt_docker_share_folder
sudo docker pull backtradercn/backtradercn-py3-runtime:1.0

# 如果独立运行(内含crontab)
sudo docker run --name backtradercn-py3 -e TZ="Asia/Shanghai" -v /etc/localtime:/etc/localtime  -v /home/bt_docker_share_folder:/home/bt_docker_share_folder --privileged --ulimit memlock=-1 --net=host -td backtradercn/backtradercn-py3-runtime:1.0 /bin/bash

# 如果(内含crontab)还需要链接外部的mysql数据库docker
sudo docker run --name backtradercn-py3 -e TZ="Asia/Shanghai" -v /etc/localtime:/etc/localtime  -v /home/bt_docker_share_folder:/home/bt_docker_share_folder --privileged=true --ulimit memlock=-1  --link mysql80:mysql  -td backtradercn/backtradercn-py3-runtime:1.0 /usr/sbin/init


copy "backtradercn-1.0-py3.7-linux-x86_64.egg" to the share folder: /home/bt_docker_share_folder
sudo docker exec -it backtradercn-py3 bash
cd /home/bt_docker_share_folder
python -m easy_install backtradercn-1.0-py3.7-linux-x86_64.egg 
cd /usr/local/python3/lib/python3.7/site-packages/backtradercn-1.0-py3.7-linux-x86_64.egg
cp *.so  /usr/lib64/
cp pystrategy.so backtradercn/






### 配置定时启动关闭md,td
copy files 
start_ctp.md.sh
start_ctp.td.sh
start_register_center.sh

################
# cat /home/bt_docker_share_folder/start_daemon.sh 
#!/bin/bash

./stop_daemon.sh

cd /home/bt_docker_share_folder/

echo `date "+%Y-%m-%d %H:%M:%S"`  start_register_center...
./start_register_center.sh
echo start_register_center: `date "+%Y-%m-%d %H:%M:%S"` >> ./start.log

sleep 2s
echo `date "+%Y-%m-%d %H:%M:%S"`  start_ctp.md.sh..
./start_ctp.md.sh
echo start_ctp.md.sh: `date "+%Y-%m-%d %H:%M:%S"` >> ./start.log


sleep 8s
echo `date "+%Y-%m-%d %H:%M:%S"`  start_ctp.td.sh..
./start_ctp.td.sh
echo start_ctp.td.sh: `date "+%Y-%m-%d %H:%M:%S"` >> ./start.log




# cat /home/bt_docker_share_folder/stop_daemon.sh
#!/bin/bash
#yum install psmisc
killall RegistryCenterServer
echo stop register_center: `date "+%Y-%m-%d %H:%M:%S"` >> ./start.log
killall ctp_md_daemon
echo stop ctp_md_daemon: `date "+%Y-%m-%d %H:%M:%S"` >> ./start.log
killall ctp_td_daemon
echo stop ctp_td_daemon: `date "+%Y-%m-%d %H:%M:%S"` >> ./start.log



#定时 crontab
#crontab -e




55 8 * * 1-5 cd /home/bt_docker_share_folder/auto;./start_daemon.sh
33 11 * * 1-5 cd /home/bt_docker_share_folder/auto;./stop_daemon.sh
#week 1-5, 13:20 PM to 15:10PM
55 12 * * 1-5 cd /home/bt_docker_share_folder/auto;./start_daemon.sh
17 15 * * 1-5 cd /home/bt_docker_share_folder/auto;./stop_daemon.sh
#week 1-6, 20:50 PM to 03:10AM
55 20 * * 1-5 cd /home/bt_docker_share_folder/auto;./start_daemon.sh
17 03 * * 1-6 cd /home/bt_docker_share_folder/auto;./stop_daemon.sh

54 16 * * 1-5 cd /home/bt_docker_share_folder/auto;./stop_daemon.sh


1 04 * * 1-6  /home/bt_docker_share_folder/auto/zip_and_mv.sh &
















# 策略示例:

cerebro = bt.Cerebro()
    cerebro.addstrategy(Resample)

    store = CtpStore(
        source_id='ctp',
        account_id='101065', # 参数含义参考课程讲解  https://edu.csdn.net/course/detail/24668
        app_id='ctp_store',  # 需要保证app_id在全系统的唯一性,并且长度不超过32bytes
        register_center_address='localhost:50051',
        location_ip='127.0.0.1',
        grpc_address='localhost:50056',
        paper_trading=0,
        offline=False,
        cachefile_valid_seconds=300,
        detect_position_change_timer=300,
        print_debug=True,
    )
    broker = store.getbroker()
    cerebro.setbroker(broker)

    instrumentId = "hc2110"
    from backtradercn.backfill import load_csv_candles, load_csv_ticks

    # 加载实时tick数据并预先填充历史数据
    # 填充历史来自backtradercn-ctp_collector产生的分钟线,使用load_csv_candles加载
    # 当然如果机器够快,硬盘够大,也可以使用load_csv_ticks加载历史tick
    data0 = store.getdata(dataname=instrumentId,
                          qcheck=0.5,
                          historical=False,
                          # backfill_from=load_csv_ticks(
                          #     datapath=r"/home/bt_docker_share_folder/ctp_test_cases/tick_folder/%s.csv" % instrumentId,
                          #     dataname=instrumentId,
                          #     fromdate=datetime.datetime.now() - datetime.timedelta(days=30),
                          #     todate=datetime.datetime.now(),
                          #     timeframe=bt.TimeFrame.Ticks,
                          #     compression=1
                          # ),
                          backfill_from=load_csv_candles(
                              datapath=os.path.join(csv_folder_path, "%s.csv" % instrumentId),
                              dataname=instrumentId,
                              fromdate=datetime.datetime.now() - datetime.timedelta(days=30),
                              todate=datetime.datetime.now(),
                              timeframe=bt.TimeFrame.Minutes,
                              compression=1
                          ),
                          timeframe=bt.TimeFrame.Minutes, compression=1,
                          fromdate=datetime.datetime.now() - datetime.timedelta(days=30),
                          todate=None,
                          )
    
    data0._name = instrumentId
    from backtradercn.CtpSessionFilter import CtpSessionFilter
    data0.addfilter(CtpSessionFilter, debug=False)
    cerebro.adddata(data0, name=instrumentId)
	# 文华k线:根据实际交易时间长度产生的
	# n=3,5,10,15,30,1*60,2*60,3*60,4*60, 支持文华k线的3分钟,5分钟,.....3小时,4小时周期
	n = 1 * 60
	from backtradercn.wenhua_resamplerfilter import WenHuaResampler, WenHuaReplayer
	dataname = data0.clone()
    dataname._name = instrumentId
    dataname.addfilter(CtpSessionFilter, debug=False)
    dataname.addfilter(WenHuaResampler,
                       timeframe=bt.TimeFrame.Seconds,
                       compression=int(n * 60),
                       )
    cerebro.adddata(dataname, name=instrumentId)
	
    #cerebro.resampledata(data0,
    #                     compression=5,
    #                     timeframe=bt.TimeFrame.Seconds)
    # cerebro.resampledata(data0,
    #                      compression=1,
    #                      timeframe=bt.TimeFrame.Days)
    cerebro.run()
    print("done")


