# Gera dados.json: Fundamentus (1 requisição, todas as ações) + Yahoo Finance (dividendos, setor, mín/máx 52s). Sem chave.
import json,datetime as dt,time,requests,pandas as pd,yfinance as yf
from io import StringIO
def n(s):
    if isinstance(s,(int,float)):return float(s)
    try:return float(str(s).replace("%","").replace(".","").replace(",",".").strip())
    except:return None
h=requests.get("https://www.fundamentus.com.br/resultado.php",headers={"User-Agent":"Mozilla/5.0"},timeout=60).text
d=pd.read_html(StringIO(h),decimal=",",thousands=".")[0]
c=lambda k:[x for x in d.columns if x.startswith(k)][0]
L={}
for _,r in d.iterrows():
    a=dict(t=r[c("Papel")],p=n(r[c("Cota")]),pl=n(r[c("P/L")]),pvp=n(r[c("P/VP")]),dy=n(r[c("Div")]),ml=n(r[c("Mrg. L")]),roe=n(r[c("ROE")]),liq=n(r[c("Liq.2")]),dbp=n(r[c("D")]),cr=n(r[c("Cresc")]))
    if not(a["liq"] and a["liq"]>=1e6 and a["pl"] and a["pl"]>0 and a["pvp"] and a["pvp"]>0 and a["roe"] and a["roe"]>0 and a["p"]):continue
    k=a["t"][:4]
    if k not in L or a["liq"]>L[k]["liq"]:L[k]=a   # 1 classe (a mais líquida) por empresa
out=[];now=pd.Timestamp.now()
for a in L.values():
    try:
        y=yf.Ticker(a["t"]+".SA");inf=y.info;hs=y.history(period="1y");v=y.dividends;v.index=v.index.tz_localize(None)
        a.update(nome=inf.get("shortName",a["t"]),setor=inf.get("sector",""),lo=float(hs["Low"].min()),hi=float(hs["High"].max()))
        v5=v[v.index>=now-pd.DateOffset(years=5)]
        a["dpa"]=round(float(v5.sum())/5,4);a["ap"]=min(5,len(set(v5.index.year)))
        a["div"]=[{"v":float(x),"d":i.strftime("%Y-%m-%d")} for i,x in v[v.index>=now-pd.DateOffset(months=18)].items()]
        out.append(a)
    except Exception as e:print("falhou",a["t"],e)
    time.sleep(.3)
json.dump({"gerado":dt.datetime.utcnow().isoformat()+"Z","acoes":out},open("dados.json","w"),ensure_ascii=False)
print(len(out),"empresas")
