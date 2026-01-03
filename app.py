import streamlit as st
import requests  # 더 강력한 접속 도구
import urllib.parse
import json
import time
import random

# ======================================================
# [설정] 비밀 금고 연동
# ======================================================
try:
    MY_NAVER_ID = st.secrets["MY_NAVER_ID"]
    MY_NAVER_SECRET = st.secrets["MY_NAVER_SECRET"]
except:
    MY_NAVER_ID = ""
    MY_NAVER_SECRET = ""

# ======================================================
# [디자인]
# ======================================================
st.set_page_config(page_title="최저가 사냥꾼", page_icon="🐢", layout="wide")

st.markdown("""
<style>
    .custom-btn {
        display: inline-flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        padding: 10px 0;
        margin-top: 5px;
        border-radius: 8px;
        text-decoration: none !important;
        color: white !important;
        font-weight: bold;
        font-size: 14px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .btn-naver { background-color: #03C75A; border: 1px solid #03C75A; }
    .btn-naver:hover { background-color: #029f48; }
    .btn-danawa { background-color: #58C623; border: 1px solid #58C623; }
    .btn-danawa:hover { background-color: #45a814; }
    .btn-enuri { background-color: #3F75FF; border: 1px solid #3F75FF; }
    .btn-enuri:hover { background-color: #2b5ae8; }
    .btn-polcent { background-color: #6c5ce7; border: 1px solid #6c5ce7; }
    .btn-polcent:hover { background-color: #5041cd; }
    a:hover { text-decoration: none; }
</style>
""", unsafe_allow_html=True)

# ======================================================
# 사이드바
# ======================================================
with st.sidebar:
    st.header("⚙️ 설정")
    default_id = MY_NAVER_ID if MY_NAVER_ID else ""
    default_secret = MY_NAVER_SECRET if MY_NAVER_SECRET else ""
    client_id = st.text_input("Client ID", value=default_id)
    client_secret = st.text_input("Client Secret", value=default_secret, type="password")
    
    st.divider()
    st.info("🐢 차단 방지를 위해 검색 속도를 일부러 늦췄습니다. (안전 모드)")

# ======================================================
# 메인 화면
# ======================================================
st.title("🐢 실시간 최저가 탐색기 (안전모드)")

col1, col2 = st.columns([4, 1])
with col1:
    keyword = st.text_input("상품명 입력", placeholder="예: 신라면 20개")
with col2:
    st.write("") 
    st.write("") 
    search_btn = st.button("검색 시작 🚀", type="primary", use_container_width=True)

# ======================================================
# 검색 로직 (Requests 라이브러리 사용)
# ======================================================
if search_btn:
    if not client_id or not client_secret:
        st.error("👈 API 키가 없습니다.")
    elif not keyword:
        st.warning("상품명을 입력해주세요.")
    else:
        st.divider()
        
        # 1. [핵심] 2초 이상 뜸들이기 (사람인 척)
        with st.spinner("🐢 네이버 문지기 눈치 보는 중... (잠시 대기)"):
            time.sleep(2) 

        # 2. 강력한 헤더 설정
        headers = {
            "X-Naver-Client-Id": client_id,
            "X-Naver-Client-Secret": client_secret,
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Connection": "keep-alive"
        }

        url = "https://openapi.naver.com/v1/search/shop.json"
        params = {
            "query": keyword,
            "display": 30,
            "start": 1,
            "sort": "asc"
        }

        try:
            # requests 라이브러리로 요청
            response = requests.get(url, headers=headers, params=params, timeout=5)
            
            # 3. 응답 코드 확인
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])

                if not items:
                    st.warning("결과가 없습니다.")
                else:
                    st.success(f"검색 성공! (총 {len(items)}개)")
                    
                    for i in range(0, len(items), 2):
                        cols = st.columns(2)
                        for j in range(2):
                            if i + j >= len(items): break
                            
                            item = items[i+j]
                            title = item['title'].replace("<b>", "").replace("</b>", "")
                            lprice = int(item['lprice'])
                            mall = item['mallName']
                            image = item['image']
                            product_id = item['productId']
                            
                            # 통합 링크 생성
                            if item['productType'] == '2':
                                naver_link = f"https://search.shopping.naver.com/product/{product_id}"
                                is_catalog = True
                            else:
                                naver_link = item['link']
                                is_catalog = False
                            
                            # 나머지 링크들
                            q_enc = urllib.parse.quote(title)
                            danawa_link = f"https://search.danawa.com/dsearch.php?query={q_enc}"
                            enuri_link = f"http://www.enuri.com/search.jsp?keyword={q_enc}"
                            polcent_link = f"https://www.google.com/search?q=site:fallcent.com+{q_enc}"
                            
                            with cols[j].container(border=True):
                                c1, c2 = st.columns([1, 2.5])
                                with c1: st.image(image, use_container_width=True)
                                with c2:
                                    if is_catalog: st.markdown(":orange[**📊 가격비교 상품**]")
                                    else: st.caption(f"판매처: {mall}")
                                    st.subheader(f"{format(lprice, ',')}원")
                                    st.text(title[:25] + "..." if len(title)>25 else title)
                                    st.write("---")
                                    b1, b2, b3, b4 = st.columns(4)
                                    with b1: st.markdown(f'<a href="{naver_link}" target="_blank" class="custom-btn btn-naver">N</a>', unsafe_allow_html=True)
                                    with b2: st.markdown(f'<a href="{danawa_link}" target="_blank" class="custom-btn btn-danawa">D</a>', unsafe_allow_html=True)
                                    with b3: st.markdown(f'<a href="{enuri_link}" target="_blank" class="custom-btn btn-enuri">E</a>', unsafe_allow_html=True)
                                    with b4: st.markdown(f'<a href="{polcent_link}" target="_blank" class="custom-btn btn-polcent">P</a>', unsafe_allow_html=True)
            
            # 에러 처리 (상세하게)
            elif response.status_code == 429:
                st.error("🚨 너무 빠릅니다! (잠시 후 다시 시도하세요)")
            elif response.status_code == 403:
                st.error("🚨 서버 접속 거부 (API 키를 확인하거나 10분 뒤 시도하세요)")
            else:
                st.error(f"오류 코드: {response.status_code}")
                st.text(response.text)

        except Exception as e:
            st.error(f"접속 오류 발생: {e}")
