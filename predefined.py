startTime = '202301215' + '000000' + '00000'  #YYYYMMDD + HHMMSS + 00000


targetChannelList = [
    {
        'name': 'YTN',
        'ID': 1,
        'main': 'https://media.naver.com/press/001',
        'categories': [
            'https://media.naver.com/newsflash/001/ElectionNation',
            'https://media.naver.com/newsflash/001/Politics',
            'https://media.naver.com/newsflash/001/Economy',
            'https://media.naver.com/newsflash/001/Society',
            'https://media.naver.com/newsflash/001/LifeCulture',
            'https://media.naver.com/newsflash/001/World',
            'https://media.naver.com/newsflash/001/It',
            'https://media.naver.com/newsflash/001/Opinion'
        ]
    },
    {
        'name': 'SBS',
        'ID': 55,
        'main': 'https://media.naver.com/press/055',
        'categories': []
    },
    {
        'name': 'KBS',
        'ID': 56,
        'main': 'https://media.naver.com/press/056',
        'categories': []
    },
    {
        'name': 'MBC',
        'ID': 214,
        'main': 'https://media.naver.com/press/214',
        'categories': []
    },
    {
        'name': 'JTBC',
        'ID': 437,
        'main': 'https://media.naver.com/press/437',
        'categories': []
    },
    {
        'name': 'TV조선',
        'ID': 448,
        'main': 'https://media.naver.com/press/448',
        'categories': []
    },
    {
        'name': '채널A',
        'ID': 449,
        'main': 'https://media.naver.com/press/449',
        'categories': []
    }
]


channelNameToID = {
    'YTN':1, 'SBS':55, 'KBS':56, 'MBC':214, 'JTBC':437, 'TV조선':448, '채널A':449 
}


channelIDToName = {
    1:'YTN', 55:'SBS', 56:'KBS', 214:'MBC', 437:'JTBC', 448:'TV조선', 449:'채널A' 
}