window.$docsify = {
        auto2top:true,
        coverpage:true,
        executeScript: true,
        loadSidebar:true,
        maxLevel: 4,
        subMaxLevel: 3,
        themeColor:'#333333',
        name:'𝒌𝒊',
        search:{maxAge: 86400000, paths: 'auto', placeholder: '🔍', noData: '无信息'},
        plugins:[ function (hook) {
                        var footer = [
                                '<footer>','<hr><small> © Ki Authors 2021-2024 | Documentation Distributed under CC-BY-4.0</small>','</footer>'
                        ].join('')
                        hook.afterEach(function (html){return html+footer})
                }
        ]
}
