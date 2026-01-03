import streamlit as st
import urllib.request
import urllib.parse
import json
import time
import random

# ======================================================
# ★ [클라우드 배포용] 비밀 금고(Secrets) 연결
# ======================================================
try:
    MY_NAVER_ID = st.secrets["MY_NAVER_ID"]
    MY_NAVER_SECRET = st.secrets["MY_NAVER_SECRET"]
except:
    # 내 컴퓨터에서 돌릴 때 (Secrets가 없을 때)
    MY_NAVER_ID = ""
    MY_NAVER_SECRET = ""

# ======================================================
# 디자인 (CSS)
# ======================================================
st.set_page_config(page_title="최저가 사냥꾼", page_icon="📉", layout="wide")

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
    .btn-naver:hover { background-color: #029f48; box-shadow: 0 4px 8px rgba(3, 199, 90, 0.3); transform: translateY(-2px); }
    .btn-danawa { background-color: #58C623; border: 1px solid #58C623; }
    .btn-danawa:hover { background-color: #45a814; box-shadow: 0 4px 8px rgba(88, 198, 35, 0.3); transform: translateY(-2px); }
    .btn-enuri { background-color: #3F75FF; border: 1px solid #3F75FF; }
    .btn-enuri:hover { background-color: #2b5ae8; box-shadow: 0 4px 8px rgba(63, 117, 255, 0.3); transform: translateY(-2px); }
    .btn-polcent { background-color: #6c5ce7; border: 1px solid #6c5ce7; }
    .btn-polcent:hover { background-color: #5041cd; box-shadow: 0 4px 8px rgba(108, 92, 231, 0.3); transform: translateY(-2px); }
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
    if default_id:
        st.success("✅ 서버 키 적용 완료!")
    else:
        st.info("💡 키를 입력하거나 Secrets를 설정하세요.")

# ======================================================
# 메인 화면
# ======================================================
st.title("📉 실시간 최저가 & 그래프 탐색기")

col1, col2 = st.columns([4, 1])
with col1:
    keyword = st.text_input("상품명 입력", placeholder="예: 신라면 20개, 갤럭시 S24")
with col2:
    st.write("")
    st.write("")
    search_btn = st.button("검색 시작 🚀", type="primary", use_container_width=True)

# ======================================================
# 검색 로직
# ======================================================
if search_btn:
    if not client_id or not client_secret:
        st.error("👈 API 키가 없습니다. (Secrets 설정을 확인하세요)")
    elif not keyword:
        st.warning("상품명을 입력해주세요.")
    else:
        st.divider()
        
        # 딜레이
        time.sleep(random.uniform(0.3, 0.8))

        encText = urllib.parse.quote(keyword)
        url = f"https://openapi.naver.com/v1/search/shop.json?query={encText}&display=30&start=1&sort=asc"

        request = urllib.request.Request(url)
        request.add_header("X-Naver-Client-Id", client_id)
        request.add_header("X-Naver-Client-Secret", client_secret)
        request.add_header("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        request.add_header("Referer", "https://shopping.naver.com/")
        request.add_header("Accept-Language", "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7")
        request.add_header("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7")

        try:
            with st.spinner(f"🔍 '{keyword}' 찾는 중..."):
                response = urllib.request.urlopen(request)
                if response.getcode() == 200:
                    data = json.loads(response.read().decode('utf-8'))
                    items = data['items']

                    if not items:
                        st.warning("결과가 없습니다.")
                    else:
                        st.success(f"검색 완료! (총 {len(items)}개)")
                        
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
                                
                                # ★ [핵심 수정] 링크 생성 규칙 변경 (/catalog/ -> /product/)
                                if item['productType'] == '2': 
                                    # 이 주소가 최신 통합 주소입니다. (오류 해결)
                                    naver_link = f"https://search.shopping.naver.com/product/{product_id}"
                                    is_catalog = True
                                else:
                                    naver_link = item['link']
                                    is_catalog = False
                                
                                search_query = urllib.parse.quote(title)
                                danawa_link = f"https://search.danawa.com/dsearch.php?query={search_query}"
                                enuri_link = f"http://www.enuri.com/search.jsp?keyword={search_query}"
                                polcent_query = urllib.parse.quote(f"site:fallcent.com {title}")
                                polcent_link = f"https://www.google.com/search?q={polcent_query}"
                                
                                with cols[j].container(border=True):
                                    c1, c2 = st.columns([1, 2.5])
                                    with c1:
                                        st.image(image, use_container_width=True)
                                    with c2:
                                        if is_catalog:
                                            st.markdown(":orange[**📊 가격비교 상품**]")
                                        else:
                                            st.caption(f"판매처: {mall}")
                                            
                                        st.subheader(f"{format(lprice, ',')}원")
                                        st.text(title[:25] + "..." if len(title)>25 else title)
                                        st.write("---")
                                        
                                        b1, b2, b3, b4 = st.columns(4)
                                        with b1: st.markdown(f'<a href="{naver_link}" target="_blank" class="custom-btn btn-naver">N</a>', unsafe_allow_html=True)
                                        with b2: st.markdown(f'<a href="{danawa_link}" target="_blank" class="custom-btn btn-danawa">D</a>', unsafe_allow_html=True)
                                        with b3: st.markdown(f'<a href="{enuri_link}" target="_blank" class="custom-btn btn-enuri">E</a>', unsafe_allow_html=True)
                                        with b4: st.markdown(f'<a href="{polcent_link}" target="_blank" class="custom-btn btn-polcent">P</a>', unsafe_allow_html=True)

                else:
                    st.error("API 접속 실패")
        except Exception as e:
            if "HTTP Error 403" in str(e) or "HTTP Error 429" in str(e):
                st.error("🚨 네이버 서버 차단됨 (잠시 대기 필요)")
            else:
                st.error(f"오류 발생: {e}")
