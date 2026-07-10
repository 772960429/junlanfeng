// 所有页面的翻译数据
const translations = {
    en: {
        // 导航
        'nav.about': 'About',
        'nav.publications': 'Publications',
        'nav.patents': 'Patents',
        'nav.experience': 'Experience',
        'nav.awards': 'Awards',
        // ===== 页面标题 =====
        'site.title': 'Junlan Feng – Chief Scientist, China Mobile Group',
        // ===== 导航栏 =====
        'site.name': 'Junlan Feng – Chief Scientist, China Mobile Group',

        // ===== 侧边栏 =====
        'sidebar.name': 'Junlan Feng',
        'sidebar.title': 'IEEE Fellow | Chief Scientist',
        'sidebar.company': 'China Mobile Group',
        'sidebar.scholar': 'Google Scholar',
        'sidebar.dblp': 'DBLP',
        'sidebar.orcid': 'ORCID',
        'sidebar.cv': '[CV]',
        'cv.link': 'CV_JunlanFeng_EN.pdf', // 英文简历路径
        
        // 首页 (index.html)
        'about.title': 'About',
        'about.intro': 'AI scientist and technology leader with nearly 30 years of experience across conversational AI, network intelligence, AI platforms, and safe foundation models. Chief Scientist of China Mobile Group; former Chair of LF Networking, the world\'s largest open-source networking community. Led the development of the Jiutian AI Platform and foundation-model technologies, supporting 4,000+ production use cases, 30+ enterprise and government clients across 9 sectors, and services reaching over one billion users.',
        'about.research': 'Research:',
        'about.research.text': '200+ academic papers; 6,800+ citations; 100+ authorized patents and 200+ pending patent applications; 1 co-authored book.',
        'about.leadership': 'Leadership & Impact:',
        'about.leadership.text': '20+ awards; 100+ keynote/invited talks; 4,000+ AI production use cases; 30+ major enterprise deployments.',
        'about.tech.leadership': 'Research and Technology Leadership:',
        'about.conversational.ai': 'Conversational AI:',
        'about.conversational.ai.text': 'At AT&T Labs Research, pioneered WebTalk, an early system for automatically building dialogue services from web content. Later led China Mobile\'s customer-service intelligence program, including the Eva intelligent customer-service system.',
        'about.network.intelligence': 'Network Intelligence:',
        'about.network.intelligence.text': 'Led China Mobile\'s network-intelligence program and key technologies for autonomous networks, supporting the evolution of autonomous-network capabilities and large-scale intelligent operations.',
        'about.jiutian': 'Jiutian AI Platform and Foundation Models:',
        'about.jiutian.text': 'Chief engineer of the Jiutian AI Platform, Jiutian AI middle platform, and Jiutian foundation-model core technologies. The platform supports large-scale AI production deployment across communications, energy, chemicals, aviation, healthcare, government services, and other sectors.',
        'about.industrial.ai': 'Industrial AI Deployment:',
        'about.industrial.ai.text': 'Chief technical leader for major AI platform and foundation-model projects with PetroChina, China National Chemical Corporation, Chinese PLA General Hospital, China Eastern Airlines, TravelSky, Gansu Provincial Government, and Heilongjiang Provincial Government.',
        'about.news': 'Recent news',
        
        // 出版物 (publications.html)
        'publications.title': 'Selected Publications',
        'publications.note': 'For a complete list, please browse my',
        'publications.note.link': 'Google Scholar',
        'pub.1': 'Robust Sentiment Detection on Twitter from Biased and Noisy Data',
        'pub.1.detail': 'COLING, 2010; 1,430+ citations.',
        'pub.2': 'Network Topology Optimization via Deep Reinforcement Learning',
        'pub.2.detail': 'IEEE Transactions on Communications, 2023; 61 citations, Impact Factor: 8.3.',
        'pub.3': 'Network Meets ChatGPT: Intent Autonomous Management, Control and Operation',
        'pub.3.detail': 'Journal of Communications and Information Networks, 2023; 84 citations, Impact Factor: 4.7.',
        'pub.4': 'Hybrid prompt-driven large language model for robust state-of-charge estimation of multitype Li-ion batteries',
        'pub.4.detail': '2024; 35 citations, Impact Factor: 9.78.',
        'pub.5': 'A survey of transformer-based multimodal pre-trained modals',
        'pub.5.detail': 'Journal of Neurocomputing, 2023; 65 citations, Impact Factor: 6.5.',
        'pub.6': 'Federated learning over coupled graphs',
        'pub.6.detail': '2023; 51 citations, Impact Factor: 7.27.',
        'pub.7': 'A survey on deep learning for cellular traffic prediction',
        'pub.7.detail': 'Intelligent Computing (Science Partner Journals), 2024; 52 citations, Impact Factor: 3.7.',
        'pub.8': 'JT-SAFE-V2: Safety-by-Design Foundation Model with World-Context Data',
        'pub.8.detail': 'arXiv:2605.24414, 2026.6',
        'pub.9': 'Measuring User Influence on Twitter Using Modified K-Shell Decomposition',
        'pub.9.detail': 'AAAI, 2021; 123 citations.',
        'pub.10': 'Probabilistic model-based sentiment analysis of twitter messages',
        'pub.10.detail': '2010 IEEE SLT; 121 citations.',
        'pub.11': 'A Comprehensive Survey on Long Context Language Modeling',
        'pub.11.detail': 'arXiv:2503.17407, 2025; 117 citations.',
        'pub.12': 'Deep Learning for Medication Recommendation: A Systematic Survey',
        'pub.12.detail': 'Journal of Data Intelligence, 2023; 74 citations.',
        
        // 专利 (patents.html)
        'patents.title': 'Selected Patents',
        'pat.1': 'Systems and methods for social media data mining',
        'pat.1.detail': 'US10496654B2, 208 Citations',
        'pat.2': 'Relevance recognition for a human machine dialog system contextual question',
        'pat.2.detail': 'US8639517B2, 127 Citations',
        'pat.3': 'Method of detecting potential phishing by analyzing universal resource locators',
        'pat.3.detail': 'US9521165B2, 81 Citations',
        'pat.4': 'System and method of providing a spoken dialog interface to a website',
        'pat.4.detail': 'US8949132B2, 81 Citations',
        'pat.5': 'System and method using a discriminative learning approach for question',
        'pat.5.detail': 'US8543565B2, 74 Citations',
        'pat.6': 'Method and apparatus for automatically building conversational systems',
        'pat.6.detail': 'US8718242B2, 61 Citations',
        'pat.7': 'A State-Aware Adversarial Generative Closed-Loop Scheme',
        'pat.7.detail': 'YF2401070',
        'pat.8': 'A Streaming Noisy Label Detection Method',
        'pat.8.detail': 'YF2310321',
        'pat.9': 'A Decoder-Based Generative Pre-Training Large Model Architecture',
        'pat.9.detail': 'YF2309241',
        'pat.10': 'A Context Orchestration and Management Method for Integrated Development and Operations of Communication Network Software',
        'pat.10.detail': 'YF2210005',
        'pat.11': 'Method, System, Framework, Device, and Apparatus for Holistic AI',
        'pat.11.detail': 'YF2207055',
        'pat.12': 'A Method for Context Orchestration and Management in Dev-Ops Integration of Communication Network Software',
        'pat.12.detail': 'YF2110069',
        
        // 经历 (experience.html)
        'experience.title': 'Professional Experience',
        'exp.1': '2021-Present: Chief Scientist at China Mobile Group',
        'exp.2': '2016-2021: CMR Chief Scientist, China Mobile Research Institute',
        'exp.3': '2013-2013: Architect, Big Data Product Line, IBM R&D Center',
        'exp.4': '2006-2013: Principal Researcher, AT&T Labs Research',
        'exp.5': '2001-2006: Senior Researcher, AT&T Labs Research',
        'education.title': 'Education',
        'edu.1': '1998-2001: Ph.D., Institute of Acoustics, Chinese Academy of Sciences',
        'edu.1.detail': 'Thesis: Acoustic models and decoding algorithms in natural speech recognition',
        'edu.2': '1995-1998: Master, Harbin Engineering University',
        'edu.2.detail': 'Thesis: Text-independent speaker recognition',
        'edu.3': '1990-1995: Bachelor, Shanxi University of Finance & Economics',
        'edu.3.detail': 'Information Science',
        'leadership.title': 'Professional Leadership',
        'lead.1': '2024-Present: Fellow of Chinese Institute of Communications',
        'lead.2': '2020-2023: Chairman of the Board of Linux Foundation Networking',
        'lead.3': '2020-Present: Board Member, Linux Foundation Networking',
        'lead.4': '2023-Present: Vice Chairman, China Large Model Committee of CCF',
        'lead.5': '2023-Present: Vice Chairman, China Artificial Intelligence Industry Alliance',
        'lead.6': '2020-Present: Deputy Director, AI Committee of Internet Society of China',
        'lead.7': '2023-Present: Co-Leader, Large Model Task Force, National AI Standardization Overall Group',
        'lead.8': '2009-2012: Member of IEEE Speech and Language Processing Technical Committee',
        'lead.9': '2014-2016: Member of IEEE Signal Processing Industrial Relation Committee',
        'lead.10': '2016-2018: China Natural Language Processing Committee',
        'lead.11': '10+ Years of Program committee members/Reviewers, Major Conferences of ACL, ISCA, ACM, AAAI, ICML, ICASSP, ICLR, NeurIPS, IEEE Transactions, etc.',
        'projects.national': 'Key National Projects in Past 5 Years',
        'proj.1': '2024-2025: Project Leader, Safety by Design Foundation Models (JT-Safe), 360+ Researchers',
        'proj.2': '2022-2025: Project Leader, National New-Generation AI Open Innovation Platform, 150+ Researchers and Engineers',
        'proj.3': '2022-2026: Director of Laboratory Council, National Key Laboratory of Multimedia Information Processing, 190+ Members of Technical Staff',
        'proj.4': '2019-2022: Project Leader, Cross-Domain Intelligent Orchestration Plane for Software-Defined Networking',
        'proj.5': '2020-2023: Technical Leader, Human-Computer Interaction Services: Large Scale',
        'projects.enterprise': 'Key Enterprise and Commercial Projects in Large scale in Past 3 Years',
        'ent.1': '2024-2025: Chief Technical Leader, PetroChina AI Middle Platform and Multimodal Foundation Model',
        'ent.2': '2025-2026: Chief Technical Leader, China National Chemical Corporation Industry Model and Platform',
        'ent.3': '2020-2025: Chief Technical Leader, Network Intelligence Transformation of China Mobile',
        'ent.4': '2023-2026: Chief Technical Leader, Jiutian Foundation Models',
        'ent.5': '2020-Present: Chief Technical Leader, Jiutian AI Platform and Middle Platform, China Mobile',
        'ent.6': '2021-2022: Chief Technical Leader, China Eastern Airlines Platform and Foundation Model',
        'ent.7': '2024-2026: Chief Technical Leader, TravelSky AI Platform and Customer Service',
        'ent.8': '2023-2025: Chief Technical Leader, Hospital AI Platform and Capabilities',
        
        // 奖项 (awards.html)
        'awards.title': 'Selected Honors and Awards',
        'awd.1': 'IEEE Fellow (2022)',
        'awd.2': 'National Outstanding Scientists — Strategic Scientist (2023)',
        'awd.3': 'Jiutian Large Model selected into the Top 10 National Key Foundation Technologies of Central Enterprises, First Principal Contributor',
        'awd.4': 'Jiutian AI Team awarded the "Model Central Enterprise" honorary Title (2024; team leader; no more than 10 nationwide each year)',
        'awd.5': 'Science and Technology Award for Key Technologies and Large-Scale Application of Autonomous Networks — As First Principal Contributor, First Class Prize, Science and Technology Award of China Institute of Communications',
        'awd.6': 'Jiutian AI Platform for the Communications Industry and Its Application — As First Principal Contributor, Second Prize, Science and Technology Award of China Institute of Communications',
        'awd.7': 'Distinguished Keynote Speech — IEEE, IEEE Computer Society, and IEEE Communication Society Technical Committee on Big Data (2019)',
        'awd.8': 'AT&T CTO Award (2009; 8 recipients across AT&T)',
        'awd.9': 'Multiple China Mobile Group Top Technical Awards: For work on Jiutian AI Platform, Jiutian Intelligent Recommendation Platform, Network intelligence, and Intelligent speech technologies',
    },
    zh: {
        // 导航
        'nav.about': '关于',
        'nav.publications': '出版物',
        'nav.patents': '专利',
        'nav.experience': '经历',
        'nav.awards': '荣誉',
        // ===== 页面标题 =====
        'site.title': '冯俊兰 – 中国移动集团首席科学家',

        // ===== 导航栏 =====
        'site.name': '冯俊兰 – 中国移动',
        

        // ===== 侧边栏 =====
        'sidebar.name': '冯俊兰',
        'sidebar.title': 'IEEE Fellow | 首席科学家',
        'sidebar.company': '中国移动集团',
        'sidebar.scholar': '谷歌学术',
        'sidebar.dblp': 'DBLP',
        'sidebar.orcid': 'ORCID',
        'sidebar.cv': '[简历]',
        'cv.link': 'CV_JunlanFeng_CN.pdf', // 中文简历路径
        
        // 首页
        'about.title': '关于我',
        'about.intro': 'AI科学家和技术领导者，拥有近30年对话式AI、网络智能、AI平台和安全基础模型领域经验。中国移动集团首席科学家；曾任全球最大开源网络社区LF Networking董事会主席。领导九天AI平台和基础模型技术研发，支撑4000+生产用例、覆盖9个行业的30+企业和政府客户，服务超过10亿用户。',
        'about.research': '学术研究：',
        'about.research.text': '200+学术论文；6800+引用；授权专利100+和专利申请200+；1本合著书籍。',
        'about.leadership': '领导力与影响：',
        'about.leadership.text': '20+奖项；100+主旨/特邀报告；4000+AI生产用例；30+大型企业部署。',
        'about.tech.leadership': '研究与技术领导力：',
        'about.conversational.ai': '对话式AI：',
        'about.conversational.ai.text': '在AT&T Labs Research期间，开创了WebTalk系统——早期从网页内容自动构建对话服务的系统。后来领导中国移动客服智能化项目，包括Eva智能客服系统。',
        'about.network.intelligence': '自智网络：',
        'about.network.intelligence.text': '领导中国移动网络智能化项目和自智网络关键技术，支撑自智网络能力演进和大规模智能运维。',
        'about.jiutian': '九天AI平台与基础模型：',
        'about.jiutian.text': '九天AI平台、九天AI中台和九天基础模型核心技术的总工程师。平台支撑通信、能源、化工、航空、医疗、政务等多行业大规模AI生产部署。',
        'about.industrial.ai': '产业AI部署：',
        'about.industrial.ai.text': '担任中石油、中国化学、解放军总医院、东方航空、中航信、甘肃省政府、黑龙江省政府等重大AI平台和基础模型项目的首席技术负责人。',
        'about.news': '最新动态',
        
        // 出版物
        'publications.title': '代表性出版物',
        'publications.note': '完整列表请浏览我的',
        'publications.note.link': '谷歌学术',
        'pub.1': '从有偏和噪声数据中进行鲁棒的Twitter情感检测',
        'pub.1.detail': 'COLING, 2010; 1430+引用。',
        'pub.2': '基于深度强化学习的网络拓扑优化',
        'pub.2.detail': 'IEEE Transactions on Communications, 2023; 61引用，影响因子: 8.3。',
        'pub.3': '网络遇ChatGPT：意图自主管理、控制与运维',
        'pub.3.detail': 'Journal of Communications and Information Networks, 2023; 84引用，影响因子: 4.7。',
        'pub.4': '混合提示驱动的大语言模型用于多类型锂离子电池鲁棒荷电状态估计',
        'pub.4.detail': '2024; 35引用，影响因子: 9.78。',
        'pub.5': '基于Transformer的多模态预训练模型综述',
        'pub.5.detail': 'Journal of Neurocomputing, 2023; 65引用，影响因子: 6.5。',
        'pub.6': '耦合图上的联邦学习',
        'pub.6.detail': '2023; 51引用，影响因子: 7.27。',
        'pub.7': '蜂窝流量预测的深度学习综述',
        'pub.7.detail': 'Intelligent Computing (Science Partner Journals), 2024; 52引用，影响因子: 3.7。',
        'pub.8': 'JT-SAFE-V2：基于世界上下文数据的安全设计基础模型',
        'pub.8.detail': 'arXiv:2605.24414, 2026.6',
        'pub.9': '使用改进K-Shell分解衡量Twitter用户影响力',
        'pub.9.detail': 'AAAI, 2021; 123引用。',
        'pub.10': '基于概率模型的Twitter消息情感分析',
        'pub.10.detail': '2010 IEEE SLT; 121引用。',
        'pub.11': '长上下文语言建模综合综述',
        'pub.11.detail': 'arXiv:2503.17407, 2025; 117引用。',
        'pub.12': '药物推荐的深度学习：系统综述',
        'pub.12.detail': 'Journal of Data Intelligence, 2023; 74引用。',
        
        // 专利
        'patents.title': '代表性专利',
        'pat.1': '用于社交媒体数据挖掘的系统和方法',
        'pat.1.detail': 'US10496654B2, 208次引用',
        'pat.2': '人机对话系统上下文问题相关性识别',
        'pat.2.detail': 'US8639517B2, 127次引用',
        'pat.3': '通过分析统一资源定位符检测潜在网络钓鱼的方法',
        'pat.3.detail': 'US9521165B2, 81次引用',
        'pat.4': '提供网站口语对话界面的系统和方法',
        'pat.4.detail': 'US8949132B2, 81次引用',
        'pat.5': '使用判别学习方法处理问题的系统和方法',
        'pat.5.detail': 'US8543565B2, 74次引用',
        'pat.6': '自动构建对话系统的方法和装置',
        'pat.6.detail': 'US8718242B2, 61次引用',
        'pat.7': '一种状态感知的对抗生成闭环方案',
        'pat.7.detail': 'YF2401070',
        'pat.8': '一种流式噪声标签检测方法',
        'pat.8.detail': 'YF2310321',
        'pat.9': '基于解码器的生成式预训练大模型架构',
        'pat.9.detail': 'YF2309241',
        'pat.10': '一种面向通信网络软件研运一体化的上下文编排管理方法',
        'pat.10.detail': 'YF2210005',
        'pat.11': '整体AI的方法、系统、框架、设备和装置',
        'pat.11.detail': 'YF2207055',
        'pat.12': '通信网络软件研运一体化中的上下文编排管理方法',
        'pat.12.detail': 'YF2110069',
        
        // 经历
        'experience.title': '工作经历',
        'exp.1': '2021-至今：中国移动集团首席科学家',
        'exp.2': '2016-2021：中国移动研究院首席科学家',
        'exp.3': '2013-2013：IBM研发中心大数据产品线架构师',
        'exp.4': '2006-2013：AT&T （贝尔）实验室研究中心（美国）主任研究员',
        'exp.5': '2001-2006：AT&T （贝尔）实验室研究中心（美国）高级研究员',
        'education.title': '教育背景',
        'edu.1': '1998-2001：中国科学院声学研究所 博士',
        'edu.1.detail': '论文：自然语音识别中声学模型和解码算法研究',
        'edu.2': '1995-1998：哈尔滨工程大学 硕士',
        'edu.2.detail': '论文：与文本无关的讲话者识别',
        'edu.3': '1990-1995：山西财经大学信息管理系',
        'edu.3.detail': '信息科学',
        'leadership.title': '专业领导职务',
        'lead.1': '2024-至今：中国通信学会会士',
        'lead.2': '2020-2023年：Linux网络基金会（LFN）董事会主席',
        'lead.3': '2020-至今：Linux网络基金会（LFN）董事会成员',
        'lead.4': '2023-至今：中国计算机协会大模型论坛副主席',
        'lead.5': '2023-至今：中国人工智能产业联盟副理事长',
        'lead.6': '2020-至今：中国互联网协会人工智能工委会副主任委员',
        'lead.7': '2023-至今：中国国家人工智能标准化总体组大模型专题组联合组长',
        'lead.8': '2009-2012：IEEE语音与语言处理技术委员会成员',
        'lead.9': '2014-2016：IEEE信号处理产业关系委员会委员',
        'lead.10': '2016-2018：中国自然语言处理专委会',
        'lead.11': '10+年担任ACL、ISCA、ACM、AAAI、ICML、ICASSP、ICLR、NeurIPS、IEEE Transactions等主要会议及期刊的程序委员会委员/审稿人。',
        'projects.national': '近5年重点国家级项目',
        'proj.1': '2024-2025：项目负责人，安全设计基础模型（JT-Safe），360+研究人员',
        'proj.2': '2022-2025：项目负责人，国家新一代AI开放创新平台，150+研究人员和工程师',
        'proj.3': '2022-2026：实验室理事会主任，多媒体信息处理国家重点实验室，190+技术人员',
        'proj.4': '2019-2022：项目负责人，软件定义网络跨域智能编排平面',
        'proj.5': '2020-2023：技术负责人，人机交互服务：大规模',
        'projects.enterprise': '近3年重点企业级与商业项目（大规模）',
        'ent.1': '2024-2025：首席技术负责人，中石油AI中台与多模态基础模型',
        'ent.2': '2025-2026：首席技术负责人，中国化学工业模型与平台',
        'ent.3': '2020-2025：首席技术负责人，中国移动网络智能化转型',
        'ent.4': '2023-2026：首席技术负责人，九天基础模型',
        'ent.5': '2020-至今：首席技术负责人，中国移动九天AI平台与中台',
        'ent.6': '2021-2022：首席技术负责人，东方航空平台与基础模型',
        'ent.7': '2024-2026：首席技术负责人，中航信AI平台与客服',
        'ent.8': '2023-2025：首席技术负责人，医院AI平台与能力',
        
        // 奖项
        'awards.title': '代表性荣誉与奖项',
        'awd.1': 'IEEE Fellow (2022)',
        'awd.2': '国家卓越工程师——战略科学家 (2023)',
        'awd.3': '九天大模型入选央企十大前沿技术，第一主要贡献者',
        'awd.4': '九天AI团队获"央企楷模"荣誉称号（2024；团队负责人；全国每年不超过10个）',
        'awd.5': '自智网络关键技术及规模化应用科学技术奖——第一主要贡献者，一等奖，中国通信学会科学技术奖',
        'awd.6': '面向通信行业的九天AI平台及其应用——第一主要贡献者，二等奖，中国通信学会科学技术奖',
        'awd.7': '杰出主题演讲——IEEE、IEEE计算机学会和IEEE通信学会大数据技术委员会 (2019)',
        'awd.8': 'AT&T CTO奖 (2009；全AT&T共8人获奖)',
        'awd.9': '多项中国移动集团技术一等奖：九天AI平台、九天智能推荐平台、网络智能化、智能语音技术等',
    }
};

// 获取当前语言
function getCurrentLang() {
    return localStorage.getItem('lang') || 'en';
}

// 设置语言
function setLanguage(lang) {
    localStorage.setItem('lang', lang);
    document.documentElement.lang = lang;
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (translations[lang] && translations[lang][key]) {
            // 如果是输入框，设置placeholder或value
            if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                if (el.hasAttribute('placeholder')) {
                    el.placeholder = translations[lang][key];
                } else {
                    el.value = translations[lang][key];
                }
            } else {
                el.innerHTML = translations[lang][key];
            }
        }
    });
    // 更新按钮状态
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.lang === lang);
    });
    // 更新HTML lang属性
    document.documentElement.lang = lang;
}

// 切换语言
function switchLanguage(lang) {
    if (lang === getCurrentLang()) return;
    setLanguage(lang);
}