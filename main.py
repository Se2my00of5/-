import vk_api


def authorize():
    log = open('pass.txt', 'r')
    login = log.readline().strip()
    password = log.readline().strip()
    return vk_api.VkApi(login, password)


vk_session = authorize()
vk_session.auth()


def count_user_friends(user):
    count = vk_api.vk_request_one_param_pool(
        vk_session,
        'users.get',
        key='user_id',
        values=[user],
        default_values={'fields': 'counters'}
    )
    if 'deactivated' in count[0][user][0]:
        return -2
    return count[0][user][0]['counters']['friends']


def id_user_friends(user):
    quan = count_user_friends(user)
    if quan == -2:
        return -2
    friends = vk_api.vk_request_one_param_pool(
        vk_session,
        'friends.get',
        key='user_id',
        values=[user],
        default_values={'count': quan}
    )
    try:
        a = set(friends[0][user]['items'])
    except Exception:
        return -1
    else:
        return a


def id_members_group(group_id, quan):
    members = vk_api.vk_request_one_param_pool(
        vk_session,
        'groups.getMembers',
        key='group_id',
        values=[group_id],
        default_values={'count': 1000}
    )
    members_id = members[0][group_id]['items']
    quan = int(min(quan, int(members[0][group_id]['count'])))
    off = 1000
    while quan >= off:
        members = vk_api.vk_request_one_param_pool(
            vk_session,
            'groups.getMembers',
            key='group_id',
            values=[group_id],
            default_values={'count': min(1000, quan - off), 'offset': off}
        )
        off += 1000
        members_id += members[0][group_id]['items']
    return set(members_id)


def friends1_members_group(group_id):  # количество друзей участника группы, которые тоже учатники данной группы
    members = id_members_group(group_id, 1e4)
    friends_member = dict()
    close_prof = set()
    close_members = dict()
    for now in members:
        iuf = id_user_friends(now)
        if iuf == -1:
            friends_member[now] = -1
            close_prof.add(now)
            close_members[now] = 0
        elif iuf != -2:
            friends_member[now] = members & iuf
    return friends_close_profile(friends_member, close_prof, close_members)


def top_quanitity_friends(group_id):
    friends_member = friends1_members_group(group_id)
    key_maxs = 0
    top_memb_friends = dict()
    for now in friends_member:
        if type(friends_member[now]) == type(key_maxs):
            top_memb_friends[now] = friends_member[now]
        else:
            top_memb_friends[now] = (friends_member[now])
    dele = []
    for i in top_memb_friends:
        if type(top_memb_friends[i]) == type(key_maxs):
            dele.append(i)
    for i in dele:
        top_memb_friends.pop(i)
    top_memb_friends = sorted(top_memb_friends.items(), key=lambda x: len(x[1]), reverse=True)

    return top_memb_friends


def friends_close_profile(friends_member, close_prof, close_members):
    for now in friends_member:
        t = set()
        if friends_member[now] != -1:
            t = close_prof & friends_member[now]
            for k in t:
                close_members[k] += 1

    for now in close_prof:
        friends_member[now] = close_members[now]
    return friends_member


def count_rebra(a):
    s = list()
    for i in range(len(a)):
        d = list(map(int, a[i][1]))
        for j in range(len(d)):
            m = min(a[i][0], d[j])
            m1 = max(a[i][0], d[j])
            s.append([m, m1])
    return len(s)


'''
a = top_quanitity_friends('nyichevsegotovo')
print('top_1')
print(a[0][0], len(a[0][1]))
print('top_2')
print(a[1][0], len(a[1][1]))
print('top_3')
print(a[2][0], len(a[2][1]))
print('кол-во человек в паблике')
print(len(a))
print(a)
'''
infile = open('tags.txt', 'r')
n = int(infile.readline().strip())
for q in range(n):
    tag = infile.readline().strip()
    fe = tag + '.txt'
    outfile = open(fe, 'w+')
    a = top_quanitity_friends(tag)
    print(count_rebra(a), file=outfile)
    for i in range(len(a)):
        print(a[i][0], file=outfile)
        print('\t', a[i][1], file=outfile)
