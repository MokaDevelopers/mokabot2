module.exports = {
	
	// 站点配置
	
	base: '/mokabot2/',
	lang: 'zh-CN',
    title: 'mokabot2',
    description: 'mokabot是一个多用途QQ群机器人。',
	
	head: [
		['link', { rel: 'icon', href: '/images/logo.png' }],
		["link", { rel: "stylesheet", href: "https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@5/css/all.min.css" }],
	],
	
	// Dev 配置项
	
	host: '127.0.0.1',
	port: 8082,
	
	// markdown 配置
	
	markdown: {
		lineNumbers: true,
	},
	
	// 主题配置
	
	theme: '@vuepress/theme-default',
	
	themeConfig: {
        logo: '/images/logo.png',

        repo: 'MokaDevelopers/mokabot2',
        docsDir: 'docs',
        editLinks: true,
        editLinkText: '在 GitHub 上编辑此页',

		nav: [
			{ text: '主页', link: '/',},
			{ text: '插件', link: '/plugins/' },
			{ text: '设置', link: '/settings/' },
			{ text: '深入', link: '/advanced/' },
			{ text: '常见问题', link: '/questions/' },
            {
                text: '外部链接',
                ariaLabel: '外部链接',
                items: [
                    { text: 'Nonebot2', link: 'https://github.com/nonebot/nonebot2' },
                    { text: 'go-cqhttp', link: 'https://github.com/Mrs4s/go-cqhttp' },
                ],
            },
		],

		sidebar: {
            '/plugins/': [
                {
                    title: '插件',
                    collapsable: false,
                    sidebar: "auto",
                    children: [
                        '',
						'ELF_RSS2',
						'FG2',
						'mai_bot',
						'mb2pkg_arcaea',
						'mb2pkg_bandori',
						'mb2pkg_epic7',
						'mb2pkg_url_parse',
						'mb2pkg_vndb',
						'nonebot_plugin_statistical',
						'mb2pkg_choice',
                        'mokabot_translation',
                    ]
                }
            ],
            '/settings/': [
                {
                    title: '设置',
                    collapsable: false,
                    sidebar: "auto",
                    children: [
                        '',
                        'plugin_switches',
                        'alias',
                        'positive_msg',
                    ]
                }
            ],
			'/advanced/': [
                {
                    title: '深入',
                    collapsable: false,
                    sidebar: "auto",
                    children: [
                        '',
						'whats_webapi',
                        'prediction'
                    ]
                }
            ],
			'/questions/': [
                {
                    title: '常见问题',
                    collapsable: false,
                    sidebar: "auto",
                    children: [
                        '',
                        'why_not_found',
                        'how_add',
                        'how_close'
                    ]
                }
            ]
		}
    },

    // 插件配置

    plugins: [
        "@vuepress/plugin-back-to-top",
        "@vuepress/plugin-medium-zoom",
    ],
}