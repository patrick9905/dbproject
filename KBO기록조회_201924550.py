import psycopg2
from psycopg2 import sql

con = psycopg2.connect(
    database='sample2023',
    user='db2023',
    password='db!2023',
    host='::1',
    port='5432'
)
cursor = con.cursor()
def register_audience():
    id = input("사용자 ID을 입력하세요: ")
    name = input("사용자 이름을 입력하세요: ")
    password = input("비밀번호를 입력하세요: ")
    insert_audience_query = '''INSERT INTO audience(id, name, password)
    VALUES (%s, %s, %s) RETURNING id;
    '''
    cursor.execute(insert_audience_query, (id, name, password))
    con.commit()
    print("회원가입이 완료되었습니다.")
def login():
    global logged_id
    while True:
        id = input("사용자 ID을 입력하세요: ")
        password = input("비밀번호를 입력하세요: ")
        query = sql.SQL("SELECT * FROM audience WHERE id = {} AND password = {}").format(
            sql.Literal(id), sql.Literal(password)
        )
        cursor.execute(query)
        result_audience = cursor.fetchone()

        query_player = sql.SQL("SELECT * FROM player WHERE id = {} AND password = {}").format(
            sql.Literal(id), sql.Literal(password)
        )
        cursor.execute(query_player)
        result_player = cursor.fetchone()

        query_director = sql.SQL("SELECT * FROM director WHERE id = {} AND password = {}").format(
            sql.Literal(id), sql.Literal(password)
        )
        cursor.execute(query_director)
        result_director = cursor.fetchone()


        if result_audience:
            print("Login successful! welcome audience")
            logged_id=result_audience
            return True, "audience"
        elif result_player:
            print("Login successful! welcome player")
            return True, "player"
        elif result_director:
            logged_id = result_director
            print("Login successful! welcome director")
            return True, "director"
        else:
            print("Login failed. Please try again.")

def menu_audience():
    while True:
        print("1.전체 기록조회 2. 즐겨찾기 0. 이전으로")
        z = int(input())
        if z == 1:
            while True:
                print("기록조회 1.타자  2. 투수  3. 수비 4. 주루 0.이전으로")
                y = int(input())
                if y == 1:
                    order_by = input(
                        "정렬 기준을 입력하세요 (타율 : avg, 타석 : pa, 타수 : ab, 안타 : hit, 2루타 : 2b, 3루타 : 3b, 홈런 : hr, 타점: rbi): ")
                    ascending = input("오름차순 정렬을 원하면 y, 내림차순 정렬을 원하면 n을 입력하세요: ").lower() == 'y'
                    show_stat_hitter(order_by, ascending)
                    continue
                elif y == 2:
                    order_by = input(
                        "정렬 기준을 입력하세요 (평균자책점 : era, 승리 : win, 패배 : lose, 세이브 : save, 삼진 : so, 이닝 : inning): ")
                    ascending = input("오름차순 정렬을 원하면 y, 내림차순 정렬을 원하면 n을 입력하세요: ").lower() == 'y'
                    show_stat_peacher(order_by, ascending)
                    continue
                elif y == 3:
                    order_by = input(
                        "정렬 기준을 입력하세요 (경기수 : game, 도루시도 : steeltry, 도루성공 : steel, 도루실패 : steelfail, 주루사 : oob, 견제사 : pko): ")
                    ascending = input("오름차순 정렬을 원하면 y, 내림차순 정렬을 원하면 n을 입력하세요: ").lower() == 'y'
                    show_stat_running(order_by, ascending)
                    continue
                elif y == 4:
                    order_by = input(
                        "정렬 기준을 입력하세요 (경기수 : game, 선발경기 : game_start, 이닝 : inning, 폴아웃 : putout, 실책 : error, 어시스트 : assist, 홈런 : hr, 타점: rbi): ")
                    ascending = input("오름차순 정렬을 원하면 y, 내림차순 정렬을 원하면 n을 입력하세요: ").lower() == 'y'
                    show_stat_defence(order_by, ascending)
                    continue
                elif y == 0:
                    break
        elif z == 2:
             favorites()
        elif z==0:
            break

def favorites():
    global logged_id
    while True:
        print("1. 즐겨찾기 등록 2. 즐겨찾기 조회 0. 이전으로 " )
        x=int(input())
        if x==1:
            print("즐겨찾기 등록은 선수만 가능합니다.")
            data=input()
            a_id=logged_id[0]
            insert_query = sql.SQL("INSERT INTO favorite (a_id, data) VALUES (%s, %s);")
            cursor.execute(insert_query, (a_id, data))
            con.commit()
            print("즐겨찾기에 추가되었습니다.")
        elif x==2:

            a_id = logged_id[0]

            peacher_query = """
                           SELECT  peacher.p_name,peacher.team,peacher.era,peacher.win,peacher.lose,peacher.save,peacher.hold, peacher.so,peacher.inning
                           FROM favorite
                           LEFT JOIN peacher ON favorite.data = peacher.p_name
                           WHERE favorite.a_id = %s;
                       """
            cursor.execute(peacher_query, (a_id,))
            peacher_info = cursor.fetchall()

            hitter_query = """
                        SELECT  hitter.h_name,hitter.team,hitter.pos,hitter.avg,hitter.pa,hitter.ab,hitter.hit, hitter."2b", hitter."3b",hitter.hr,hitter.rbi
                        FROM favorite
                        LEFT JOIN hitter ON favorite.data = hitter.h_name
                        WHERE favorite.a_id = %s;
                                   """
            cursor.execute(hitter_query, (a_id,))
            hitter_info= cursor.fetchall()

            runner_query = """
            SELECT  running.r_name,running.team,running.game,running.steeltry,running.steel,running.steelfail,running.oob,running.pko
            FROM favorite
            LEFT JOIN running ON favorite.data = running.r_name
            WHERE favorite.a_id = %s;
                       """
            cursor.execute(runner_query, (a_id,))
            running_info = cursor.fetchall()

            defence_query = """
            SELECT  defence.d_name,defence.team,defence.pos,defence.inning,defence.error,defence.game,defence.game_start, defence.putout,defence.assist
            FROM favorite
            LEFT JOIN defence ON favorite.data = defence.d_name
            WHERE favorite.a_id = %s;
                               """
            cursor.execute(defence_query, (a_id,))
            defence_info = cursor.fetchall()

            print("\n즐겨찾기 조회 결과 (투수) :  평균자책점 , 승리 , 패배 , 세이브 , 삼진 , 이닝 ")
            for peacher in peacher_info:
                if all(peacher):
                    print(peacher)

            print("\n즐겨찾기 조회 결과 (타격): 타율 , 타석 , 타수 , 안타 , 2루타 , 3루타 , 홈런 , 타점")
            for hitter in hitter_info:
                if any(hitter):
                    print(hitter)

            print("\n즐겨찾기 조회 결과 (주루): 경기수 , 도루시도 , 도루성공 , 도루실패 , 주루사 , 견제사")
            for running in running_info:
                if any(running):
                    print(running)

            print("\n즐겨찾기 조회 결과 (수비):")
            for defence in defence_info:
                if any(defence):
                    print(defence)
        elif x==0:
            break


def show_stat_hitter(order_by, ascending=True):
    player_query =  sql.SQL("SELECT * FROM hitter ORDER BY {} {}").format(
        sql.Identifier(order_by), sql.SQL("ASC" if ascending else "DESC")
    )
    cursor.execute(player_query)
    players = cursor.fetchall()

    print("\n선수 조회 결과:")
    print("{:<10} {:<10} {:<5} {:<5} {:<5} {:<5} {:<5} {:<5} {:<5} {:<5} {:<5}".format( "이름", "팀", "포지션", "타율", "타석", "타수", "안타", "2루타", "3루타", "홈런", "타점"))
    for player in players:
        print(" {:<10} {:<5} {:<5} {:<8} {:<6} {:<6} {:<6} {:<6} {:<6} {:<6} {:<6} ".format(*player[1:]))

def show_stat_peacher(order_by, ascending=True):
    peacher_query = sql.SQL("SELECT * FROM peacher ORDER BY {} {}").format(
        sql.Identifier(order_by), sql.SQL("ASC" if ascending else "DESC")
    )
    cursor.execute(peacher_query)
    peachers = cursor.fetchall()

    print("\n선수 조회 결과:")
    print(
        " {:<5} {:<10} {:<5} {:<5} {:<5} {:<5} {:<5} {:<5} {:<5} ".format("이름", "팀", "평균자책점", "승리",
                                                                                           "패배", "세이브", "홀드", "타자수",
                                                                                           "이닝"))
    for player in peachers:
        print("{:<5} {:<10} {:<6} {:<7} {:<7} {:<6} {:<7} {:<6} {:<6}   ".format(*player[1:]))

def show_stat_running(order_by, ascending=True):
    runner_query = sql.SQL("SELECT * FROM running ORDER BY {} {}").format(
        sql.Identifier(order_by), sql.SQL("ASC" if ascending else "DESC")
    )
    cursor.execute(runner_query)
    players = cursor.fetchall()

    print("\n선수 조회 결과:")
    print(
        " {:<5} {:<10} {:<5} {:<5} {:<5} {:<5} {:<5} {:<5}  ".format( "이름", "팀", "게임수", "도루시도",
                                                                                           "도루허용", "도루실패", "주루사", "견제사"))
    for player in players:
        print("{:<5} {:<10} {:<5} {:<9} {:<8} {:<6} {:<6} {:<6}   ".format(*player[1:]))

def show_stat_defence(order_by, ascending=True):
    player_query = sql.SQL("SELECT * FROM defence ORDER BY {} {}").format(
        sql.Identifier(order_by), sql.SQL("ASC" if ascending else "DESC"))
    cursor.execute(player_query)
    players = cursor.fetchall()

    print("\n선수 조회 결과:")
    print(
        "{:<6} {:<10} {:<5} {:<5} {:<5} {:<5} {:<5} {:<5} {:<5} ".format( "이름", "팀", "포지션", "이닝",
                                                                                           "에러", "경기", "선발경기", "풋아웃",
                                                                                           "어시스트"))
    for player in players:
        print(" {:<5} {:<8} {:<6} {:<8} {:<6} {:<6} {:<6} {:<6} {:<6}  ".format(*player[1:]))

def menu_player():
    while True:
        print("1.전체 기록조회 0. 이전으로")
        z = int(input())
        if z == 1:
            while True:
                print("기록조회 1.타자  2. 투수  3. 수비 4. 주루 0.이전으로")
                y = int(input())
                if y == 1:
                    order_by = input("정렬 기준을 입력하세요 (타율 : avg, 타석 : pa, 타수 : ab, 안타 : hit, 2루타 : 2b, 3루타 : 3b, 홈런 : hr, 타점: rbi): ")
                    ascending = input("오름차순 정렬을 원하면 y, 내림차순 정렬을 원하면 n을 입력하세요: ").lower() == 'y'
                    show_stat_hitter(order_by,ascending)
                    continue
                elif y == 2:
                    order_by = input(
                        "정렬 기준을 입력하세요 (평균자책점 : era, 승리 : win, 패배 : lose, 세이브 : save, 삼진 : so, 이닝 : inning): ")
                    ascending = input("오름차순 정렬을 원하면 y, 내림차순 정렬을 원하면 n을 입력하세요: ").lower() == 'y'
                    show_stat_peacher(order_by, ascending)
                    continue
                elif y == 3:
                    order_by = input(
                        "정렬 기준을 입력하세요 (경기수 : game, 도루시도 : steeltry, 도루성공 : steel, 도루실패 : steelfail, 주루사 : oob, 견제사 : pko): ")
                    ascending = input("오름차순 정렬을 원하면 y, 내림차순 정렬을 원하면 n을 입력하세요: ").lower() == 'y'
                    show_stat_running(order_by,ascending)
                    continue
                elif y == 4:
                    order_by = input(
                        "정렬 기준을 입력하세요 (경기수 : game, 선발경기 : game_start, 이닝 : inning, 폴아웃 : putout, 실책 : error, 어시스트 : assist, 홈런 : hr, 타점: rbi): ")
                    ascending = input("오름차순 정렬을 원하면 y, 내림차순 정렬을 원하면 n을 입력하세요: ").lower() == 'y'
                    show_stat_defence(order_by,ascending)
                    continue
                elif y == 0:
                    break
        elif z==0:
            break
def menu_director():
    while True:
        print("1.전체 기록조회 2. 트레이드 3. 선발 변경 4. 선발 조회 0. 이전으로")
        z = int(input())
        if z == 1:
            while True:
                print("기록조회 1.타자  2. 투수  3. 수비 4. 주루 0.이전으로")
                y = int(input())
                if y == 1:
                    order_by = input(
                        "정렬 기준을 입력하세요 (타율 : avg, 타석 : pa, 타수 : ab, 안타 : hit, 2루타 : 2b, 3루타 : 3b, 홈런 : hr, 타점: rbi): ")
                    ascending = input("오름차순 정렬을 원하면 y, 내림차순 정렬을 원하면 n을 입력하세요: ").lower() == 'y'
                    show_stat_hitter(order_by, ascending)
                    continue
                elif y == 2:
                    order_by = input(
                        "정렬 기준을 입력하세요 (평균자책점 : era, 승리 : win, 패배 : lose, 세이브 : save, 삼진 : so, 이닝 : inning): ")
                    ascending = input("오름차순 정렬을 원하면 y, 내림차순 정렬을 원하면 n을 입력하세요: ").lower() == 'y'
                    show_stat_peacher(order_by, ascending)
                    continue
                elif y == 3:
                    order_by = input(
                        "정렬 기준을 입력하세요 (경기수 : game, 도루시도 : steeltry, 도루성공 : steel, 도루실패 : steelfail, 주루사 : oob, 견제사 : pko): ")
                    ascending = input("오름차순 정렬을 원하면 y, 내림차순 정렬을 원하면 n을 입력하세요: ").lower() == 'y'
                    show_stat_running(order_by, ascending)
                    continue
                elif y == 4:
                    order_by = input(
                        "정렬 기준을 입력하세요 (경기수 : game, 선발경기 : game_start, 이닝 : inning, 폴아웃 : putout, 실책 : error, 어시스트 : assist, 홈런 : hr, 타점: rbi): ")
                    ascending = input("오름차순 정렬을 원하면 y, 내림차순 정렬을 원하면 n을 입력하세요: ").lower() == 'y'
                    show_stat_defence(order_by, ascending)
                    continue
                elif y == 0:
                    break
        elif z == 2:
            trades()
        elif z==3:
            starter_change()
        elif z==4:
            show_starter()
        elif z==0:
            break

def trades():
    director_team = get_director_team()

    opponent_team = input("교환할 상대 팀을 입력하세요: ")
    director_player_name = input(f"{director_team} 팀에서 교환할 선수 이름을 입력하세요: ")
    opponent_player_name = input(f"{opponent_team} 팀에서 교환할 선수 이름을 입력하세요: ")
    try:
        # 트랜잭션 시작
        cursor.execute("BEGIN;")

        move_player_to_team(cursor, director_player_name, director_team, opponent_team)
        move_player_to_team(cursor, opponent_player_name, opponent_team, director_team)

        # 트랜잭션 커밋
        cursor.execute("COMMIT")
        print("트레이드가 성공적으로 완료되었습니다.")

    except Exception as e:
        # 트랜잭션 롤백
        cursor.execute("ROLLBACK")
        print(f"트레이드 중 오류가 발생하였습니다: {e}")
def get_director_team():
    global logged_id
    return logged_id[2]

def move_player_to_team(cursor, player_name,from_team, to_team):
    try:
        # 선수의 팀 정보 업데이트 쿼리 실행
        update_peacher_query = sql.SQL("""
                   UPDATE peacher
                   SET team = %s
                   WHERE p_name = %s AND team = %s
               """)
        cursor.execute(update_peacher_query, (to_team, player_name, from_team))

        # 특정 선수가 타자인 경우
        update_hitter_query = sql.SQL("""
                   UPDATE hitter
                   SET team = %s
                   WHERE h_name = %s AND team = %s
               """)
        cursor.execute(update_hitter_query, (to_team, player_name, from_team))

        # 특정 선수가 수비수인 경우
        update_defence_query = sql.SQL("""
                   UPDATE defence
                   SET team = %s
                   WHERE d_name = %s AND team = %s
               """)
        cursor.execute(update_defence_query, (to_team, player_name, from_team))

        # 특정 선수가 주루수인 경우
        update_running_query = sql.SQL("""
                   UPDATE running
                   SET team = %s
                   WHERE r_name = %s AND team = %s
               """)
        cursor.execute(update_running_query, (to_team, player_name, from_team))

        # 트랜잭션 커밋
        cursor.execute("COMMIT")

        # 각 테이블에서 영향받은 행이 없으면 해당 선수가 해당 팀에 속해 있지 않다는 의미이므로 예외 발생
        if cursor.rowcount == 0:
            raise ValueError(f"{player_name} 선수는 {from_team} 팀에 속해 있지 않습니다.")

        # 팀 변경 성공
        print(f"{player_name} 선수를 {from_team} 팀에서 {to_team} 팀으로 이동시켰습니다.")
    except Exception as e:
        # 트랜잭션 롤백
        cursor.execute("ROLLBACK")
        print(f"선수 이동 중 오류 발생: {e}")
def starter_change():
    team = get_director_team()
    cursor = con.cursor()

    # 선발 라인업을 가져오기 위한 SELECT 쿼리
    select_lineup_query = sql.SQL("""
            SELECT * FROM selection
            WHERE team = %s
        """)

    # 선발 라인업이 이미 존재하는지 확인
    cursor.execute(select_lineup_query, (team,))
    existing_lineup = cursor.fetchall()

    if existing_lineup:
        # 선발 라인업이 이미 존재하면 업데이트
        print("선발 라인업이 이미 존재합니다. 업데이트를 진행합니다.")
        update_lineup_query = sql.SQL("""
                UPDATE selection
                SET name = %s,
                    pos = %s
                WHERE team = %s AND "order" = %s
            """)
        # 선발투수의 이름만 입력받음
        pitcher_name = input(f"{team} 팀의 선발투수 이름: ")
        # 마지막 로우는 선발투수로 고정
        last_order = str(0)

        cursor.execute(update_lineup_query, (pitcher_name, '투수', team, last_order))
        for i in range(9):
            player_name = input(f"{team} 팀의 {i + 1}번 타자 이름: ")
            player_position = input(f"{team} 팀의 {i + 1}번 타자의 포지션: ")

            cursor.execute(update_lineup_query, (player_name, player_position,team,str(i+1) ))



    else:
        # 선발 라인업이 존재하지 않으면 새로 삽입
        print("선발 라인업이 존재하지 않습니다. 새로운 라인업을 삽입합니다.")
        insert_lineup_query = sql.SQL("""
                INSERT INTO selection (name, "order", team,pos)
                VALUES (%s, %s, %s,%s)
            """)
        # 선발투수의 이름만 입력받음
        pitcher_name = input(f"{team} 팀의 선발투수 이름: ")
        # 마지막 로우는 선발투수로 고정
        last_order = str(0)

        cursor.execute(insert_lineup_query, (pitcher_name, last_order, team, '투수'))

        for i in range(9):
            player_name = input(f"{team} 팀의 {i + 1}번 타자 이름: ")
            player_position = input(f"{team} 팀의 {i + 1}번 타자의 포지션: ")

            cursor.execute(insert_lineup_query, (player_name, str(i+1),team,player_position  ))



    con.commit()

def show_starter():
    team = get_director_team()
    cursor = con.cursor()

    # 선발 라인업 조회 쿼리
    select_lineup_query = sql.SQL("""
                SELECT * FROM selection
                WHERE team = %s
                ORDER BY "order"
            """)

    # 선발 라인업 조회
    cursor.execute(select_lineup_query, (team,))
    starting_lineup = cursor.fetchall()

    if not starting_lineup:
        print(f"{team} 팀의 선발 라인업이 존재하지 않습니다.")
    else:
        print(f"{team} 팀의 선발 라인업:")
        for player in starting_lineup:
            print(f"{player[3]}번: {player[1]} ({player[2]})")

    cursor.close()
while True:
    print("kbo 선수 스탯 관리 및 조회 프로그램 입니다.\n1.로그인 2. 회원가입 0. 종료")
    x = int(input())
    if x == 1:
        success,user_type= login()
        if success:
            if user_type=="audience":
                menu_audience()
            elif user_type=="player":
                menu_player()
            elif user_type=="director":
                menu_director()
    elif x == 2:
        register_audience()
    elif x == 0:
        print("프로그램을 종료합니다.")
        break

# 연결 및 커서 종료
cursor.close()
con.close()
