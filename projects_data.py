"""
Blockchain projects data for content generation.
Contains information about all the projects to create content for.
"""

BLOCKCHAIN_PROJECTS = [
    {
        'name': 'Infinex',
        'website': 'infinex.xyz',
        'twitter_handle': '@infinex',
        'description': 'DeFi trading platform focused on perpetual futures',
        'category': 'DeFi'
    },
    {
        'name': 'Espresso',
        'website': 'espressosys.com',
        'twitter_handle': '@EspressoSys',
        'description': 'Blockchain infrastructure for decentralized sequencing',
        'category': 'Infrastructure'
    },
    {
        'name': 'Boop',
        'website': 'boop.fun',
        'twitter_handle': '@boopdotfun',
        'description': 'Social platform for blockchain interactions',
        'category': 'Social'
    },
    {
        'name': 'Somnia',
        'website': 'somnia.network',
        'twitter_handle': '@Somnia_Network',
        'description': 'High-performance blockchain for gaming and virtual worlds',
        'category': 'Gaming'
    },
    {
        'name': 'Openledger',
        'website': 'openledger.xyz',
        'twitter_handle': '@OpenledgerHQ',
        'description': 'Decentralized ledger infrastructure',
        'category': 'Infrastructure'
    },
    {
        'name': 'Sei',
        'website': 'sei.io',
        'twitter_handle': '@SeiNetwork',
        'description': 'Purpose-built Layer 1 blockchain for trading',
        'category': 'Layer 1'
    },
    {
        'name': 'Sophon',
        'website': 'sophon.xyz',
        'twitter_handle': '@sophon',
        'description': 'Entertainment-focused blockchain ecosystem',
        'category': 'Entertainment'
    },
    {
        'name': 'Soon',
        'website': 'soon.app',
        'twitter_handle': '@soon_svm',
        'description': 'Solana Virtual Machine implementation',
        'category': 'Infrastructure'
    },
    {
        'name': 'Huma Finance',
        'website': 'humafinance.com',
        'twitter_handle': '@humafinance',
        'description': 'Real-world asset tokenization platform',
        'category': 'RWA'
    },
    {
        'name': 'Sunrise',
        'website': 'sunriselayer.com',
        'twitter_handle': '@SunriseLayer',
        'description': 'Data availability layer for blockchain scalability',
        'category': 'Infrastructure'
    },
    {
        'name': 'Skate',
        'website': 'skatechain.com',
        'twitter_handle': '@skate_chain',
        'description': 'Universal app chain for multi-chain applications',
        'category': 'Infrastructure'
    },
    {
        'name': 'dYdX',
        'website': 'dydx.exchange',
        'twitter_handle': '@dYdX',
        'description': 'Decentralized derivatives exchange',
        'category': 'DeFi'
    },
    {
        'name': 'Maplestory Universe',
        'website': 'maplestoryu.com',
        'twitter_handle': '@MaplestoryU',
        'description': 'Blockchain gaming metaverse',
        'category': 'Gaming'
    },
    {
        'name': 'Camp Network',
        'website': 'campnetwork.xyz',
        'twitter_handle': '@campnetworkxyz',
        'description': 'Modular blockchain for consumer applications',
        'category': 'Infrastructure'
    },
    {
        'name': 'Arbitrum',
        'website': 'arbitrum.org',
        'twitter_handle': '@arbitrum',
        'description': 'Ethereum Layer 2 scaling solution',
        'category': 'Layer 2'
    },
    {
        'name': 'Polkadot',
        'website': 'polkadot.network',
        'twitter_handle': '@Polkadot',
        'description': 'Multi-chain blockchain protocol',
        'category': 'Layer 1'
    },
    {
        'name': 'Lombard',
        'website': 'lombard.finance',
        'twitter_handle': '@Lombard_Finance',
        'description': 'Bitcoin liquid staking protocol',
        'category': 'DeFi'
    },
    {
        'name': 'Fomo',
        'website': 'tryfomo.com',
        'twitter_handle': '@tryfomo',
        'description': 'Social trading platform',
        'category': 'Social'
    },
    {
        'name': 'Humanity Protocol',
        'website': 'humanityprot.org',
        'twitter_handle': '@Humanityprot',
        'description': 'Human identity verification protocol',
        'category': 'Identity'
    },
    {
        'name': 'Mantle',
        'website': 'mantlenetwork.io',
        'twitter_handle': '@Mantle_Official',
        'description': 'Ethereum Layer 2 with modular architecture',
        'category': 'Layer 2'
    },
    {
        'name': 'Newton',
        'website': 'magicnewton.com',
        'twitter_handle': '@MagicNewton',
        'description': 'AI-powered blockchain analytics',
        'category': 'Analytics'
    },
    {
        'name': 'Novastro',
        'website': 'novastro.xyz',
        'twitter_handle': '@Novastro_xyz',
        'description': 'Decentralized space exploration platform',
        'category': 'Utility'
    },
    {
        'name': 'Satlayer',
        'website': 'satlayer.com',
        'twitter_handle': '@satlayer',
        'description': 'Bitcoin restaking infrastructure',
        'category': 'Infrastructure'
    },
    {
        'name': 'Soul',
        'website': '0xsoulprotocol.com',
        'twitter_handle': '@0xSoulProtocol',
        'description': 'Decentralized identity and reputation system',
        'category': 'Identity'
    },
    {
        'name': 'Virtuals',
        'website': 'virtuals.io',
        'twitter_handle': '@virtuals_io',
        'description': 'AI agents marketplace for virtual interactions',
        'category': 'AI'
    }
]

# Additional metadata for content generation
PROJECT_CATEGORIES = {
    'DeFi': {
        'focus_areas': ['trading', 'liquidity', 'yield farming', 'lending', 'derivatives'],
        'key_metrics': ['TVL', 'volume', 'fees generated', 'user growth']
    },
    'Layer 1': {
        'focus_areas': ['consensus', 'scalability', 'decentralization', 'security'],
        'key_metrics': ['TPS', 'validator count', 'network effects', 'developer activity']
    },
    'Layer 2': {
        'focus_areas': ['scaling', 'fees', 'security', 'interoperability'],
        'key_metrics': ['transaction cost', 'throughput', 'bridge security', 'adoption']
    },
    'Infrastructure': {
        'focus_areas': ['developer tools', 'interoperability', 'performance', 'composability'],
        'key_metrics': ['developer adoption', 'integration count', 'performance benchmarks']
    },
    'Gaming': {
        'focus_areas': ['user experience', 'economics', 'NFTs', 'metaverse'],
        'key_metrics': ['player count', 'retention', 'in-game economy', 'asset trading']
    },
    'Social': {
        'focus_areas': ['user experience', 'content creation', 'monetization', 'community'],
        'key_metrics': ['user growth', 'engagement', 'content volume', 'creator economy']
    },
    'Identity': {
        'focus_areas': ['privacy', 'verification', 'reputation', 'compliance'],
        'key_metrics': ['verification rate', 'privacy guarantees', 'adoption by institutions']
    },
    'AI': {
        'focus_areas': ['automation', 'intelligence', 'personalization', 'efficiency'],
        'key_metrics': ['AI accuracy', 'user satisfaction', 'automation level', 'cost reduction']
    }
}

def get_project_by_name(name: str):
    """Get project data by name."""
    for project in BLOCKCHAIN_PROJECTS:
        if project['name'].lower() == name.lower():
            return project
    return None

def get_projects_by_category(category: str):
    """Get all projects in a specific category."""
    return [project for project in BLOCKCHAIN_PROJECTS if project.get('category') == category]

def get_all_categories():
    """Get list of all project categories."""
    return list(set(project.get('category', 'Unknown') for project in BLOCKCHAIN_PROJECTS))
