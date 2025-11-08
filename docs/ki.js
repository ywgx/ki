window.$docsify = {
	auto2top:true,
	coverpage:{
		'/':'_coverpage.md',
		'/en/':'en/_coverpage.md'
	},
	executeScript: true,
	loadSidebar:true,
	maxLevel: 4,
	subMaxLevel: 3,
	themeColor:'#333333',
	name:'𝒌𝒊',
	routerMode:'hash',
	alias:{
		'/en/.*/README.md':'/en/README.md',
		'/en/.*/start.md':'/en/start.md',
		'/en/.*/debug.md':'/en/debug.md',
		'/en/.*/labs.md':'/en/labs.md',
		'/en/.*/changelog.md':'/en/changelog.md',
		'/en/.*/_sidebar.md':'/en/_sidebar.md'
	},
	fallbackLanguages:['en'],
	search:{maxAge: 86400000, paths: 'auto', placeholder: '🔍 Search / 搜索', noData: 'No results / 无信息'},
	plugins:[
		function (hook) {
			var footer = [
				'<footer>','<hr><small> © Ki Authors 2021-2025 | Documentation Distributed under CC-BY-4.0</small>','</footer>'
			].join('')
			hook.afterEach(function (html){return html+footer})
		}
	]
}
