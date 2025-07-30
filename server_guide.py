#!/usr/bin/env python3
"""
ProjectMeats Server Provider Comparison Tool
============================================

Interactive tool to help choose the best server provider for ProjectMeats deployment.
Provides recommendations based on budget, location, and requirements.
"""

import sys


class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


class ServerProviderGuide:
    def __init__(self):
        self.providers = {
            'digitalocean': {
                'name': 'DigitalOcean',
                'cost_min': 20,
                'cost_max': 40,
                'specs': '2-4 vCPU, 4-8GB RAM, 50-100GB SSD',
                'pros': ['Simple one-click apps', 'Excellent documentation', 'Predictable pricing', 'Good community'],
                'cons': ['Limited enterprise features', 'Basic monitoring'],
                'setup_difficulty': 'Easy',
                'best_for': 'Small to medium businesses, first-time deployment',
                'locations': ['US', 'EU', 'Asia', 'Global'],
                'setup_url': 'https://www.digitalocean.com/products/droplets/',
                'tutorial_url': 'https://docs.digitalocean.com/products/droplets/how-to/create/',
                'rating': 9.2
            },
            'linode': {
                'name': 'Linode (Akamai)',
                'cost_min': 18,
                'cost_max': 36,
                'specs': '2-4 vCPU, 4-8GB RAM, 50-100GB SSD',
                'pros': ['Excellent performance', 'Great price/performance', 'Outstanding support', 'Developer friendly'],
                'cons': ['Smaller ecosystem', 'Fewer one-click apps'],
                'setup_difficulty': 'Easy',
                'best_for': 'Performance-focused deployments, developers',
                'locations': ['US', 'EU', 'Asia-Pacific'],
                'setup_url': 'https://www.linode.com/products/shared/',
                'tutorial_url': 'https://www.linode.com/docs/guides/getting-started/',
                'rating': 9.1
            },
            'vultr': {
                'name': 'Vultr',
                'cost_min': 20,
                'cost_max': 40,
                'specs': '2-4 vCPU, 4-8GB RAM, 50-100GB SSD',
                'pros': ['Fast NVMe SSDs', 'Global locations', 'Good value', 'Quick deployment'],
                'cons': ['Smaller support team', 'Basic documentation'],
                'setup_difficulty': 'Easy',
                'best_for': 'Global reach, fast deployment, cost-conscious',
                'locations': ['Worldwide (20+ locations)'],
                'setup_url': 'https://www.vultr.com/products/cloud-compute/',
                'tutorial_url': 'https://www.vultr.com/docs/deploy-a-new-server',
                'rating': 8.8
            },
            'aws_lightsail': {
                'name': 'AWS Lightsail',
                'cost_min': 20,
                'cost_max': 40,
                'specs': '2-4 vCPU, 4-8GB RAM, 50-100GB SSD',
                'pros': ['AWS ecosystem', 'Easy scaling to full AWS', 'Predictable pricing', 'Reliable'],
                'cons': ['More complex than competitors', 'Can get expensive'],
                'setup_difficulty': 'Medium',
                'best_for': 'AWS integration, future scaling plans',
                'locations': ['AWS Global Infrastructure'],
                'setup_url': 'https://aws.amazon.com/lightsail/',
                'tutorial_url': 'https://docs.aws.amazon.com/lightsail/latest/userguide/getting-started-with-amazon-lightsail.html',
                'rating': 8.5
            },
            'hetzner': {
                'name': 'Hetzner',
                'cost_min': 15,
                'cost_max': 30,
                'specs': '2-4 vCPU, 4-8GB RAM, 40-80GB SSD',
                'pros': ['Excellent value', 'EU data centers', 'Great performance', 'Good support'],
                'cons': ['Primarily EU focused', 'Less global presence'],
                'setup_difficulty': 'Easy',
                'best_for': 'EU-based businesses, cost-effective hosting',
                'locations': ['Germany', 'Finland', 'EU'],
                'setup_url': 'https://www.hetzner.com/cloud',
                'tutorial_url': 'https://docs.hetzner.com/cloud/servers/getting-started/creating-a-server/',
                'rating': 9.0
            }
        }
    
    def print_banner(self):
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}  ProjectMeats Server Provider Comparison{Colors.END}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    def get_requirements(self):
        print(f"{Colors.CYAN}Let's find the best server provider for your needs!{Colors.END}\n")
        
        # Budget
        print(f"{Colors.BOLD}💰 What's your monthly budget?{Colors.END}")
        print("1. Under $25/month")
        print("2. $25-50/month") 
        print("3. $50-100/month")
        print("4. Budget is not a concern")
        
        budget_choice = input(f"{Colors.YELLOW}Select (1-4): {Colors.END}").strip()
        budget_ranges = {
            '1': (0, 25),
            '2': (25, 50),
            '3': (50, 100),
            '4': (0, 1000)
        }
        budget = budget_ranges.get(budget_choice, (0, 50))
        
        # Location
        print(f"\n{Colors.BOLD}🌍 Where are your users located?{Colors.END}")
        print("1. North America")
        print("2. Europe") 
        print("3. Asia-Pacific")
        print("4. Global/Multiple regions")
        
        location_choice = input(f"{Colors.YELLOW}Select (1-4): {Colors.END}").strip()
        locations = {
            '1': 'North America',
            '2': 'Europe',
            '3': 'Asia-Pacific', 
            '4': 'Global'
        }
        preferred_location = locations.get(location_choice, 'Global')
        
        # Experience level
        print(f"\n{Colors.BOLD}🎯 What's your deployment experience?{Colors.END}")
        print("1. Beginner - Need simple setup")
        print("2. Intermediate - Some server experience")
        print("3. Advanced - Comfortable with complex setups")
        
        experience_choice = input(f"{Colors.YELLOW}Select (1-3): {Colors.END}").strip()
        experience_levels = {
            '1': 'Beginner',
            '2': 'Intermediate',
            '3': 'Advanced'
        }
        experience = experience_levels.get(experience_choice, 'Intermediate')
        
        # Special requirements
        print(f"\n{Colors.BOLD}⚙️  Any special requirements?{Colors.END}")
        print("1. Best performance")
        print("2. Easiest setup")
        print("3. Best value for money")
        print("4. Future AWS integration")
        print("5. EU data compliance")
        
        requirement_choice = input(f"{Colors.YELLOW}Select (1-5): {Colors.END}").strip()
        requirements = {
            '1': 'performance',
            '2': 'ease',
            '3': 'value',
            '4': 'aws',
            '5': 'eu_compliance'
        }
        special_requirement = requirements.get(requirement_choice, 'value')
        
        return budget, preferred_location, experience, special_requirement
    
    def score_provider(self, provider_key, provider, budget, location, experience, requirement):
        score = 0
        
        # Budget scoring
        if budget[0] <= provider['cost_min'] <= budget[1] or budget[0] <= provider['cost_max'] <= budget[1]:
            score += 30
        elif provider['cost_max'] <= budget[1]:
            score += 20
        
        # Location scoring
        provider_locations = provider['locations']
        if location == 'Global' or any(loc in ' '.join(provider_locations) for loc in [location]):
            score += 20
        elif location == 'Europe' and any('EU' in loc or 'Germany' in loc for loc in provider_locations):
            score += 20
        elif location == 'North America' and any('US' in loc for loc in provider_locations):
            score += 20
        
        # Experience scoring
        difficulty = provider['setup_difficulty']
        if experience == 'Beginner' and difficulty == 'Easy':
            score += 25
        elif experience == 'Intermediate':
            score += 20
        elif experience == 'Advanced':
            score += 15
        
        # Special requirement scoring
        if requirement == 'performance' and provider_key in ['linode', 'hetzner']:
            score += 25
        elif requirement == 'ease' and provider_key in ['digitalocean']:
            score += 25
        elif requirement == 'value' and provider_key in ['hetzner', 'vultr']:
            score += 25
        elif requirement == 'aws' and provider_key == 'aws_lightsail':
            score += 25
        elif requirement == 'eu_compliance' and provider_key == 'hetzner':
            score += 25
        
        # Base rating bonus
        score += provider['rating']
        
        return score
    
    def get_recommendations(self, budget, location, experience, requirement):
        scored_providers = []
        
        for key, provider in self.providers.items():
            score = self.score_provider(key, provider, budget, location, experience, requirement)
            scored_providers.append((score, key, provider))
        
        # Sort by score (highest first)
        scored_providers.sort(reverse=True)
        
        return scored_providers
    
    def display_recommendations(self, recommendations, budget, location, experience, requirement):
        print(f"\n{Colors.BOLD}🎯 Recommendations for your requirements:{Colors.END}")
        print(f"Budget: ${budget[0]}-${budget[1]}/month | Location: {location} | Experience: {experience}")
        print(f"{Colors.BLUE}{'='*80}{Colors.END}")
        
        for i, (score, key, provider) in enumerate(recommendations[:3], 1):
            color = Colors.GREEN if i == 1 else Colors.YELLOW if i == 2 else Colors.CYAN
            
            print(f"\n{color}{Colors.BOLD}#{i} {provider['name']} (Score: {score:.1f}/100){Colors.END}")
            print(f"   💰 Cost: ${provider['cost_min']}-${provider['cost_max']}/month")
            print(f"   ⚙️  Specs: {provider['specs']}")
            print(f"   📍 Locations: {', '.join(provider['locations'])}")
            print(f"   🎯 Best for: {provider['best_for']}")
            print(f"   ⭐ Setup difficulty: {provider['setup_difficulty']}")
            
            print(f"   {Colors.GREEN}✓ Pros:{Colors.END}")
            for pro in provider['pros']:
                print(f"     • {pro}")
            
            print(f"   {Colors.YELLOW}⚠ Cons:{Colors.END}")
            for con in provider['cons']:
                print(f"     • {con}")
            
            print(f"   🔗 Setup: {Colors.CYAN}{provider['setup_url']}{Colors.END}")
            print(f"   📖 Tutorial: {Colors.CYAN}{provider['tutorial_url']}{Colors.END}")
    
    def show_quick_setup_commands(self, top_provider):
        provider_name = top_provider[2]['name']
        print(f"\n{Colors.BOLD}🚀 Quick Setup Commands for {provider_name}:{Colors.END}")
        print(f"{Colors.BLUE}{'='*50}{Colors.END}")
        
        print(f"{Colors.CYAN}1. Create Server:{Colors.END}")
        print(f"   • Choose Ubuntu 20.04+ LTS")
        print(f"   • Select 2-4 vCPU, 4-8GB RAM plan")
        print(f"   • Add your SSH key")
        print(f"   • Select region closest to your users")
        
        print(f"\n{Colors.CYAN}2. Domain Setup:{Colors.END}")
        print(f"   • Point your domain's A record to server IP")
        print(f"   • Wait for DNS propagation (up to 24 hours)")
        
        print(f"\n{Colors.CYAN}3. Server Deployment:{Colors.END}")
        print(f"   ssh root@your-server-ip")
        print(f"   git clone https://github.com/Vacilator/ProjectMeats.git")
        print(f"   cd ProjectMeats")
        print(f"   python3 deploy_production.py")
        
        print(f"\n{Colors.GREEN}✅ Total setup time: 30-60 minutes{Colors.END}")
    
    def run(self):
        self.print_banner()
        
        try:
            budget, location, experience, requirement = self.get_requirements()
            recommendations = self.get_recommendations(budget, location, experience, requirement)
            self.display_recommendations(recommendations, budget, location, experience, requirement)
            
            if recommendations:
                self.show_quick_setup_commands(recommendations[0])
            
            print(f"\n{Colors.BOLD}💡 Pro Tip:{Colors.END}")
            print(f"All providers offer free credits for new accounts:")
            print(f"• DigitalOcean: $200 credit")
            print(f"• Linode: $100 credit") 
            print(f"• Vultr: $100 credit")
            print(f"• AWS: 12 months free tier")
            
            print(f"\n{Colors.GREEN}🎯 Ready to deploy? Run:{Colors.END}")
            print(f"{Colors.CYAN}python3 deploy_production.py{Colors.END}")
            
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Setup cancelled.{Colors.END}")
        except Exception as e:
            print(f"\n{Colors.BOLD}Error: {e}{Colors.END}")


if __name__ == "__main__":
    guide = ServerProviderGuide()
    guide.run()