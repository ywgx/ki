window.$docsify = {
        auto2top: true,
        coverpage: ['/', '/en/'],
        executeScript: true,
        loadSidebar: true,
        loadNavbar: true,
        maxLevel: 4,
        subMaxLevel: 3,
        themeColor: '#333333',
        name: '𝒌𝒊',
        alias: {
                '/en/.*/_sidebar.md': '/en/_sidebar.md',
                '/en/.*/_navbar.md': '/en/_navbar.md'
        },
        search: {
                maxAge: 86400000,
                paths: ['/', '/en/'],
                placeholder: {
                        '/': '🔍 搜索',
                        '/en/': '🔍 Search'
                },
                noData: {
                        '/': '无信息',
                        '/en/': 'No results'
                },
                pathNamespaces: ['/', '/en']
        },
        plugins: [function (hook) {
                var footer = [
                        '<footer>', '<hr><small> © Ki Authors 2021-2025 | Documentation Distributed under CC-BY-4.0</small>', '</footer>'
                ].join('')
                hook.afterEach(function (html) { return html + footer })
        }]
}
