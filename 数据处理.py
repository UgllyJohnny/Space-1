import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from docutils.nodes import header
from matplotlib.pyplot import margins
from sphinx.addnodes import index
from sympy import false

# df3yue = pd.read_excel(r"D:\工作文件\项目\GJ2024140_中国物流福田自动存储项目\正品收发存-3月份.xls", sheet_name=(0),usecols=(0,1,2,3,4,5,9))
# df3yue.dropna(axis=0,inplace=True)
# df3yue["SKU号"]= df3yue["零件号"].str.cat(df3yue["供应商代码"],sep="_")
# dfwul = pd.read_excel(r"D:\工作文件\项目\GJ2024140_中国物流福田自动存储项目\（20250319）物料档案.xls", sheet_name=(0))
# dfwul["SKU号"]= dfwul["零件号"].str.cat(dfwul["供应商代码"],sep="_")
# print(df3yue.head(), dfwul.head())
# #df3yue.to_excel(excel_writer=r"D:\工作文件\项目\GJ2024140_中国物流福田自动存储项目\python\3月.xls")
# df = pd.merge(df3yue, dfwul, on="SKU号", how="inner")
# df[['长', '宽',"高"]] = df['外包装尺寸cm'].str.split(('*'or"×"), expand=True)
# print(df.head())
# df3yue.info()
# dfwul.info()
# df.info()
# df.to_excel(excel_writer=r"D:\工作文件\项目\GJ2024140_中国物流福田自动存储项目\python\合并.xls")
df_06_09 = pd.read_csv(r"D:\工作文件\项目\GJ2024140_中国物流福田自动存储项目\数据\20250306新数据\保管台帐20240601_20240930.csv")
df_ck06_09=df_06_09[df_06_09["出库数量"]>=0]

#读取6-9月数据，并过滤掉出库数量小于=0的数据
df_rk06_09=df_06_09[(df_06_09["入库数量"].notna()) & (df_06_09["入库数量"] >= 0)]
#读取06-09月数据，并筛选出入库数据
df_10_12 = pd.read_csv(r"D:\工作文件\项目\GJ2024140_中国物流福田自动存储项目\数据\20250306新数据\保管台帐20241001_20241231.csv")
df_ck10_12=df_10_12[df_10_12["出库数量"]>=0]
#读取10-12月数据，并过滤掉出库数量小于=0的数据
df_rk10_12=df_10_12[(df_10_12["入库数量"].notna()) & (df_10_12["入库数量"] >= 0)]
#读取10-12月数据，并筛选出入库数据

df_06_12 = pd.concat([df_ck06_09, df_ck10_12], axis=0)
#纵向合并6-12月份---出库------数据
df_06_12["SKU号"]= df_06_12["零件号"].str.cat(df_06_12["供应商代码"],sep="_")
df_06_12.drop(["入库数量","总库存结存数"],axis=1,inplace=True)
#----------------------物料单提取操作
df_wl=pd.read_excel(r"D:\工作文件\项目\GJ2024140_中国物流福田自动存储项目\数据\（20250324）物料档案整理.xls")
df_wl["SKU号"]= df_wl["零件号"].str.cat(df_wl["供应商代码"],sep="_")
df_wl.drop(["零件号","零件名称","供应商代码"],axis=1,inplace=True)
df_wl.info()
#-----------------------物料单和订单合并
df_hb= pd.merge(df_06_12,df_wl, on="SKU号", how="inner")

#------------------------合并表的计算
df_hb["整托出库"]=df_hb["出库数量"]//df_hb["托规格（件）"]
df_hb["整箱出库"]=df_hb["出库数量"]%df_hb["托规格（件）"]//df_hb["原包装量"]
df_hb["拆箱出库"]=df_hb["出库数量"]%df_hb["托规格（件）"]%df_hb["原包装量"]
df_hb["出库总箱数"] = np.ceil(df_hb["出库数量"] / df_hb["原包装量"]).astype(int)
df_hb["整托存储"]=df_hb["期初数量"]//df_hb["托规格（件）"]
df_hb["整托存储全"] = np.ceil(df_hb["期初数量"] / df_hb["托规格（件）"]).astype(int)
df_hb["整托出库件数"]=df_hb["整托出库"]*df_hb["托规格（件）"]
df_hb["整箱出库件数"]=df_hb["整箱出库"]*df_hb["原包装量"]

df_hb.info()
#####==============================入库数据操作
df_rk06_12 = pd.concat([df_rk06_09, df_rk10_12], axis=0)
#纵向合并6-12月份---入库------数据

df_rk06_12["SKU号"]= df_rk06_12["零件号"].str.cat(df_rk06_12["供应商代码"],sep="_")
df_rk06_12.drop(["出库数量","总库存结存数"],axis=1,inplace=True)
#----------------------物料单提取操作
#-----------------------物料单和订单合并
df_rk_hb= pd.merge(df_rk06_12,df_wl, on="SKU号", how="inner")
#------------------------入库合并表的计算

df_rk_hb["整托入库"]=df_rk_hb["入库数量"]//df_rk_hb["托规格（件）"]
df_rk_hb["整托入库全"] = np.ceil(df_rk_hb["入库数量"] / df_rk_hb["托规格（件）"]).astype(int)

#-----------------------------------(日期维度)入库汇总
df_rk=pd.pivot_table(
    df_rk_hb,
    values=["整托入库","整托入库全","SKU号"],
    index=["日期"],
    aggfunc={"整托入库":"sum","整托入库全":"sum",'SKU号':pd.Series.nunique}

).rename(columns={"SKU号":"入库SKU数","整托入库":"整托入库总数","整托入库全":"整托+半托入库总数"})
df_rk["平均SKU入库托数"]=df_rk["整托+半托入库总数"]//df_rk["入库SKU数"]


#------------------------------------------------------------------------
#=========================================提取库存数据（主要是删掉不同订单的库存重复记录，仅保留当日库存的最大值，作为当天出库前的存储量）
#----筛选库存期初数量，每天每个品的期初数量最大值
# 获取每个日期每个SKU的最大库存量值
df_hb_kc1 = (
    df_hb.groupby(['日期', 'SKU号'], sort=False)['整托存储全']
    .max()
    .reset_index()
    .sort_values('日期')
)

# 合并回原始数据获取完整记录（使用merge而不是loc）
df_hb_kc = pd.merge(
    df_hb_kc1,
    df_hb,
    on=['日期', 'SKU号', '整托存储全'],
    how='left'
)

# 去重（如果有多个相同最大值的记录）
df_hb_kc = df_hb_kc.drop_duplicates(subset=['日期', 'SKU号'])

df_hb_kc.info()

#--------------------------------------------------------------------------------

#-----------------------------------(供货商维度)存储汇总
df_cc_ghs=pd.pivot_table(
    df_hb_kc,
    values=["整托存储","整托存储全","SKU号"],
    index=["供应商简称"],
    aggfunc={"整托存储":"sum","整托存储全":"sum",'SKU号':pd.Series.nunique}

).rename(columns={"SKU号":"存储SKU数","整托存储":"整托总数","整托存储全":"整托+半托总数"})
#------提取7于30日数据
df_cc_0730= df_hb_kc[df_hb_kc['日期'].str.contains('-07-30')]

#-----------------------------------(7月30日，每品托盘数量维度)存储汇总
df_cc_ts = pd.crosstab(
    index=df_cc_0730['整托存储全'],
    columns="托数合计",
    values=df_cc_0730['整托存储全'],
    aggfunc='sum',
    margins=True
)

#7月30日------------------(供货商维度)存储汇总
df_cc_0730fx=pd.pivot_table(
    df_cc_0730,
    values=["整托存储","整托存储全","SKU号"],
    index=["供应商简称"],
    aggfunc={"整托存储":"sum","整托存储全":"sum",'SKU号':pd.Series.nunique}

).rename(columns={"SKU号":"存储SKU数","整托存储":"整托总数","整托存储全":"整托+半托总数"})

#------提取-07-30|-07-08|-07-02|-07-24|-08-17|-09-24|-09-30|-11-08|-12-17|-12-20|-12-24数据
df_cc_max= df_hb_kc[df_hb_kc['日期'].str.contains('-07-30|-07-08|-07-02|-07-24|-08-17|-09-24|-09-30|-11-08|-12-17|-12-20|-12-24')]
#7月30日------------------(供货商维度)存储汇总
df_cc_max_fx=pd.pivot_table(
    df_cc_max,
    values=["整托存储全"],
    index=["供应商简称"],
    columns="日期",
    aggfunc="sum"

).rename(columns={"SKU号":"存储SKU数","整托存储":"整托总数","整托存储全":"整托+半托总数"})

#-----------------------------------(日期维度)存储汇总
df_cc=pd.pivot_table(
    df_hb_kc,
    values=["整托存储","整托存储全","SKU号"],
    index=["日期"],
    aggfunc={"整托存储":"sum","整托存储全":"sum",'SKU号':pd.Series.nunique}

).rename(columns={"SKU号":"存储SKU数","整托存储":"整托总数","整托存储全":"整托+半托总数"})
df_cc["平均单SKU储量"]=df_cc["整托+半托总数"]//df_cc["存储SKU数"]

#------------------------------（日期维度）出库数量汇总，SKU数汇总
df_ck1=pd.pivot_table(
    df_hb,
    values=["出库数量","整托出库件数","整箱出库件数","SKU号","对应单据号"],
    index=["日期"],
    aggfunc={"出库数量":"sum","整托出库件数":"sum","整箱出库件数":"sum","SKU号":pd.Series.nunique,'对应单据号':pd.Series.nunique}

).rename(columns={"SKU号":"日动销SKU数","出库数量":"日出库合计","整托出库件数":"整托出库合计","整箱出库件数":"整箱出库合计","对应单据号":"日订单数量"})
df_ck2=pd.pivot_table(
    df_hb,
    values="对应单据号",
    index=["日期"],
    aggfunc="count"
).rename(columns={"对应单据号":"日订单行数"})
df_ck=pd.concat([df_ck1,df_ck2],axis=1)
df_ck["单均行数"]=df_ck["日订单行数"]/df_ck["日订单数量"]
df_ck["整托出库占比"]=df_ck["整托出库合计"]/df_ck["日出库合计"]#计算整托出库占比
df_ck["整箱出库占比"]=df_ck["整箱出库合计"]/df_ck["日出库合计"]#计算整箱出库炸逼
df_ck["拆箱出库占比"]=1-df_ck["整箱出库占比"]-df_ck["整托出库占比"]#计算拆箱出库占比
#------------------------------（SKU维度）出库数量汇总，SKU数汇总
df_cksku=pd.pivot_table(
    df_hb,
    values=["出库数量","整托出库","整箱出库","拆箱出库","出库总箱数","整托出库件数","整箱出库件数"],
    index=["SKU号"],
    aggfunc="sum"

)

#--------------------------------取7月3日行数最多，12月13日出库量最大
df_0703= df_hb[df_hb['日期'].str.contains('-07-03')]
df_1213=df_hb[df_hb['日期'].str.contains('-12-13')]
#============================================
df_ck0703=pd.pivot_table(
    df_0703,
    values=["整托出库","整箱出库","拆箱出库","出库数量"],
    index=["对应单据号"],
    aggfunc="sum"

).rename(columns={"整托出库":"整托出库数量","整箱出库":"整箱出库数量","拆箱出库":"拆箱出库数量","出库数量":"出库数量合计"})

#-------------------------------
#df_06_12.to_excel(excel_writer=r"D:\工作文件\项目\GJ2024140_中国物流福田自动存储项目\python\合并.xlsx")
#将零件号和供应商代码合并为SKU号-------------------------------------------------------------
df_rq1=pd.pivot_table(
    df_06_12,
    values=["SKU号","出库数量","对应单据号"],
    index=["日期"],
    aggfunc={"SKU号":"count","出库数量":"sum",'对应单据号':pd.Series.nunique}

).rename(columns={"SKU号":"日动销SKU数","出库数量":"日出库总量","对应单据号":"日订单数量"})
#'对应单据号':pd.Series.nunique,不重复技术表示，重复计数用count
df_hs=pd.pivot_table(
    df_06_12,
    values=["对应单据号"],
    index=["日期"],
    aggfunc="count"

).rename(columns={"对应单据号":"日订单行数"})
df_rq=pd.concat([df_rq1,df_hs],axis=1)
df_rq["单均行数"]=df_rq["日订单行数"]/df_rq["日订单数量"]
#-----------------------------------------------------------------
# df_tj=pd.pivot_table(
#     df_rq,
#     values=["日动销SKU数","日出库总量","日订单数量","日订单行数","单均行数"],
#     index=["日期"],
#     aggfunc={
#         "日动销SKU数": ["max", "min", "mean"],
#         "日出库总量": ["max", "min", "mean"],
#         "日订单数量": ["max", "min", "mean"],
#         "日订单行数": ["max", "min", "mean"],
#         "单均行数": ["max", "min", "mean"]
#     }
# )
df_tj = df_rq.agg({
    "日动销SKU数": ["max", "min", "mean"],
    "日出库总量": ["max", "min", "mean"],
    "日订单数量": ["max", "min", "mean"],
    "日订单行数": ["max", "min", "mean"],
    "单均行数": ["max", "min", "mean"]
})


# 创建一个 ExcelWriter 对象，用于写入多个工作表
with pd.ExcelWriter(r"D:\工作文件\项目\GJ2024140_中国物流福田自动存储项目\python\全部汇总.xlsx") as writer:
    # 写入 df_rq 到默认工作表（Sheet1）
    df_rq.to_excel(writer, sheet_name="汇总")

    # 写入 df_tj 到另一个工作表
    df_tj.to_excel(writer, sheet_name="统计")
    df_wl.to_excel(writer, sheet_name="物料")
    df_06_12.to_excel(writer, sheet_name="6-12全部出库订单")
    df_rk06_12.to_excel(writer, sheet_name="6-12全部入库订单")
    df_hb.to_excel(writer, sheet_name="合并")
    df_rk_hb.to_excel(writer, sheet_name="入库合并")
    df_rk.to_excel(writer, sheet_name="入库统计")
    df_cc.to_excel(writer, sheet_name="存储统计")
    df_ck.to_excel(writer, sheet_name="出库统计")
    df_0703.to_excel(writer, sheet_name="7月3日（行数最多日）")
    df_1213.to_excel(writer, sheet_name="12月13日（出库数量最多日）")
    df_ck0703.to_excel(writer, sheet_name="12月13日（0703出库统计）")
    df_cksku.to_excel(writer, sheet_name="12月13日（SKU维度订单结构）")
    df_cc_0730fx.to_excel(writer, sheet_name="7月30日（供货商存储结构分析）")
    df_cc_max_fx.to_excel(writer, sheet_name="max（供货商存储结构分析）")
    df_hb_kc.to_excel(writer, sheet_name="库存订单筛选汇总")
    df_cc_ts.to_excel(writer, sheet_name="7月30日每个SKU的存储托数占比")