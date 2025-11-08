window.$docsify = {
	auto2top:true,
	coverpage:true,
	executeScript: true,
	loadSidebar:true,
	maxLevel: 4,
	subMaxLevel: 3,
	themeColor:'#333333',
	name:'𝒌𝒊',
	search:{maxAge: 86400000, paths: 'auto', placeholder: '🔍 Search / 搜索', noData: 'No results / 无信息'},
	plugins:[
		function (hook) {
			var footer = [
				'<footer>','<hr><small> © Ki Authors 2021-2025 | Documentation Distributed under CC-BY-4.0</small>','</footer>'
			].join('')
			hook.afterEach(function (html){return html+footer})
		},
		function (hook) {
			var BUTTON_ID = 'lang-toggle';
			var zhHash = '#/';
			var enHash = '#/en/';

			function getLang(){
				return decodeURIComponent(window.location.hash || zhHash).indexOf(enHash) === 0 ? 'en' : 'zh';
			}

			function ensureButton(){
				var btn = document.getElementById(BUTTON_ID);
				if(!btn){
					btn = document.createElement('button');
					btn.id = BUTTON_ID;
					btn.type = 'button';
					btn.setAttribute('aria-label','Toggle language');
					document.body.appendChild(btn);
				}
				return btn;
			}

			function updateLabel(){
				var btn = document.getElementById(BUTTON_ID);
				if(!btn) return;
				if(getLang() === 'en'){
					btn.textContent = 'English · 中文';
					btn.dataset.lang = 'en';
				}else{
					btn.textContent = '中文 · English';
					btn.dataset.lang = 'zh';
				}
			}

			function toggleLanguage(){
				var next = getLang() === 'en' ? zhHash : enHash;
				window.location.hash = next;
			}

			hook.ready(function (){
				var btn = ensureButton();
				btn.addEventListener('click', toggleLanguage);
				updateLabel();
			});

			hook.doneEach(updateLabel);
			window.addEventListener('hashchange', updateLabel);
		}
	]
}
