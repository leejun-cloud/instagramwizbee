import os
import json
import datetime
from create_card_news import generate_card
from style_blueprint import extract_blueprint

DATA_FILE = "book_data.json"

# Curated list of 30 Books for the Batch Generation
BOOK_LIST = [
    {"title": "자제력의 원리 (자유론)", "excerpt": "가장 소중한 것은 자신의 삶을 스스로 통제하는 능력이다."},
    {"title": "명상록 (마르쿠스 아우렐리우스)", "excerpt": "우리의 삶은 우리의 생각이 만드는 것이다."},
    {"title": "죽음의 수용소에서 (빅터 프랭클)", "excerpt": "삶에 의미가 있다면 고통에도 의미가 있다."},
    {"title": "성공하는 사람들의 7가지 습관", "excerpt": "자극과 반응 사이에는 선택이라는 공간이 있다."},
    {"title": "아주 작은 습관의 힘", "excerpt": "1%의 개선이 1년 뒤에는 37배의 성장이 된다."},
    {"title": "군주론 (마키아벨리)", "excerpt": "지도자는 사랑받기보다 두려움의 대상이 되는 것이 안전하다."},
    {"title": "월든 (헨리 데이비드 소로)", "excerpt": "자신의 꿈을 향해 당당히 나아가는 자는 성공을 마주할 것이다."},
    {"title": "인간 관계론 (데일 카네기)", "excerpt": "비판은 아무런 소용이 없다. 그것은 상대를 방어적으로 만든다."},
    {"title": "몰입 (황농문)", "excerpt": "생각의 끈을 놓지 않는 것이 문제 해결의 시작이다."},
    {"title": "어떻게 살 것인가 (유시민)", "excerpt": "삶의 의미는 내가 직접 만들어야 하는 것이다."},
    {"title": "침묵의 기술 (조제프 앙투안)", "excerpt": "말해야 할 때를 아는 것보다 침묵해야 할 때를 아는 것이 어렵다."},
    {"title": "총, 균, 쇠 (재레드 다이아몬드)", "excerpt": "민족의 역사는 환경적 차이에서 비롯되었다."},
    {"title": "사피엔스 (유발 하라리)", "excerpt": "우리는 보이지 않는 허구를 믿는 유일한 종이다."},
    {"title": "정의란 무엇인가 (마이클 샌델)", "excerpt": "공동의 선을 추구할 때 정의가 실현된다."},
    {"title": "연금술사 (파울로 코엘료)", "excerpt": "간절히 원하면 온 우주가 너를 도와준단다."},
    {"title": "논어", "excerpt": "배우고 때맞추어 익히니 또한 기쁘지 아니한가."},
    {"title": "차라투스트라는 이렇게 말했다", "excerpt": "나의 영혼을 초인으로 만들어라."},
    {"title": "돈의 속성 (김승호)", "excerpt": "돈은 인격체처럼 다루어야 머무른다."},
    {"title": "보도 섀퍼의 돈", "excerpt": "경제적 자유는 책임을 수락하는 데서 온다."},
    {"title": "그릿 (엔젤라 더크워스)", "excerpt": "천재성보다 중요한 것은 끝까지 해내는 그릿이다."},
    {"title": "부의 추월차선", "excerpt": "부자가 되려면 시스템을 구축하라."},
    {"title": "린 스타트업", "excerpt": "작게 시작하고 빠르게 실패하며 배우라."},
    {"title": "타이탄의 도구들", "excerpt": "성공한 사람들의 아침은 루틴으로 시작된다."},
    {"title": "지대넓얕 (채사장)", "excerpt": "세계는 거대한 지식의 사슬로 연결되어 있다."},
    {"title": "넛지 (리처드 탈러)", "excerpt": "선택 설계자가 세상을 바꾼다."},
    {"title": "상실의 시대 (무라카미 하루키)", "excerpt": "죽음은 삶의 반대편이 아니라 삶의 일부로 존재한다."},
    {"title": "노인과 바다", "excerpt": "인간은 패배하기 위해 태어난 것이 아니다."},
    {"title": "페르마의 마지막 정리", "excerpt": "수학은 인류가 도달할 수 있는 가장 순수한 진리다."},
    {"title": "코스모스 (칼 세이건)", "excerpt": "우리는 별에서 온 먼지다."},
    {"title": "국가 (플라톤)", "excerpt": "동굴 밖의 진리를 보는 자가 통치해야 한다."}
]

def generate_batch(count=30):
    if not os.path.exists(DATA_FILE):
        data = []
    else:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

    # Start numbering from the next day
    start_day = max([p["day"] for p in data]) + 1 if data else 1
    # Start date from tomorrow
    start_date = datetime.date.today() + datetime.timedelta(days=1)
    
    # Pre-load style
    ref_dir = "references"
    reference_images = [os.path.join(ref_dir, f) for f in os.listdir(ref_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))] if os.path.exists(ref_dir) else []
    style_params = None
    if reference_images:
        style_params = extract_blueprint(reference_images[0])

    new_entries = []
    for i in range(min(count, len(BOOK_LIST))):
        day_num = start_day + i
        scheduled_date = (start_date + datetime.timedelta(days=i)).isoformat()
        book_info = BOOK_LIST[i]
        
        image_path = f"images/day_{day_num}.png"
        print(f"[{i+1}/{count}] Generating post for {book_info['title']} (Day {day_num}, Date {scheduled_date})...")
        
        # 1. Generate Image
        try:
            generate_card(book_info['excerpt'], image_path, style_params=style_params)
        except Exception as e:
            print(f"Image gen failed for {day_num}: {e}")
            continue

        # 2. Add to data
        entry = {
            "day": day_num,
            "scheduled_date": scheduled_date,
            "book_title": book_info['title'],
            "excerpt": book_info['excerpt'],
            "hook": f"💡 {book_info['title']}: 오늘의 한 문장",
            "caption": f"'{book_info['excerpt']}'\n\n위즈비가 전하는 오늘의 지혜입니다. ✨",
            "hashtags": "#위즈비 #Wizbee #독서 #자기계발 #명언",
            "approved": False,
            "published": False
        }
        new_entries.append(entry)

    data.extend(new_entries)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Batch Generation Complete ({len(new_entries)} posts created).")

if __name__ == "__main__":
    generate_batch(30)
