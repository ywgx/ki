window.$docsify = {
        auto2top:true,
        coverpage:true,
        executeScript: true,
        loadSidebar:true,
        maxLevel: 4,
        subMaxLevel: 3,
        themeColor:'#333333',
        name:'𝒌𝒊',
        nameLink: {
                '/zh-cn/': '#/zh-cn/',
                '/en/': '#/en/',
                '/': '#/zh-cn/'
        },
        fallbackLanguages: ['zh-cn', 'en'],
        search:{
                maxAge: 86400000,
                paths: 'auto',
                placeholder: {
                        '/zh-cn/': '🔍 搜索',
                        '/en/': '🔍 Search',
                        '/': '🔍'
                },
                noData: {
                        '/zh-cn/': '无信息',
                        '/en/': 'No Results',
                        '/': '无信息'
                }
        },
        plugins:[ function (hook) {
                        var footer = [
                                '<footer>','<hr><small> © Ki Authors 2021-2025 | Documentation Distributed under CC-BY-4.0</small>','</footer>'
                        ].join('')
                        hook.afterEach(function (html){return html+footer})
                }
        ]
}
