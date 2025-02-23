from requestcord import *
logger = Logger(level='INF')

class Bypass:
    BASE_URL = "https://discord.com/api/v9"

    @classmethod
    def fetch_onboarding_questions(cls, token: str, guild_id: str) -> Optional[Dict[str, Any]]:
        """Fetch onboarding questions for a guild."""
        endpoint = f"{cls.BASE_URL}/guilds/{guild_id}/onboarding"
        header_generator = HeaderGenerator()
        headers = header_generator.generate_headers(token)

        try:
            response = requests.get(
                endpoint,
                headers=headers,
                impersonate=header_generator.impersonate_target
            )
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to fetch questions: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error fetching questions: {e}")
            return None

    @classmethod
    def generate_random_responses(cls, questions: Dict[str, Any]) -> Tuple[List[str], Dict[str, int], Dict[str, int]]:
        """
        Returns: 
        - List of selected option IDs
        - Prompts seen with timestamps
        - Options seen with timestamps
        """
        selected_options = []
        prompts_seen = {}
        options_seen = {}
        current_time = int(time.time() * 1000)
    
        for prompt in questions.get("prompts", []):
            prompt_id = str(prompt.get("id"))
            prompts_seen[prompt_id] = current_time
            

            for option in prompt.get("options", []):
                option_id = str(option["id"])
                options_seen[option_id] = current_time
            
            if prompt["type"] == 0:
                options = prompt["options"]
                if prompt["single_select"]:
                    selected = [random.choice(options)["id"]]
                else:
                    selected = [opt["id"] for opt in random.sample(options, k=random.randint(1, len(options)))]
                
                selected_options.extend(selected)
    
        return selected_options, prompts_seen, options_seen

    @classmethod
    def onboarding(cls, token: str, guild_id: str) -> bool:
        questions = cls.fetch_onboarding_questions(token, guild_id)
        if not questions:
            return False
    
        responses, prompts_seen, options_seen = cls.generate_random_responses(questions)
        
        logger.debug(f"Submitting: {responses}")
    
        payload = {
            "onboarding_responses": responses,
            "onboarding_prompts_seen": prompts_seen,
            "onboarding_responses_seen": options_seen
        }
    
        endpoint = f"{cls.BASE_URL}/guilds/{guild_id}/onboarding-responses"
        header_generator = HeaderGenerator()
        headers = header_generator.generate_headers(token)
    
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                impersonate=header_generator.impersonate_target
            )
            if response.status_code == 200:
                logger.success("Successfully bypassed Onboarding!")
                return True
            logger.error(f"Failed: {response.status_code} - {response.text}")
            return False
        except Exception as e:
            logger.error(f"Error: {e}")
            return False

    @classmethod
    def fetch_server_rules(cls, token: str, guild_id: str) -> Optional[Dict]:
        """Get server verification requirements"""
        endpoint = f"{cls.BASE_URL}/guilds/{guild_id}/member-verification"
        header_generator = HeaderGenerator()
        headers = header_generator.generate_headers(token)
        
        try:
            response = requests.get(
                endpoint,
                headers=headers,
                impersonate=header_generator.impersonate_target
            )
            if response.status_code == 200:
                return response.json()
            logger.error(f"Failed to fetch rules: {response.status_code} - {response.text}")
            return None
        except Exception as e:
            logger.error(f"Rules fetch error: {e}")
            return None

    @classmethod
    def generate_rule_response(cls, rules_data: Dict) -> Dict:
        """Generate payload that matches server's verification form"""
        return {
            "version": rules_data["version"],
            "form_fields": [
                {
                    "field_type": field["field_type"],
                    "label": field["label"],
                    "description": field.get("description"),
                    "required": field["required"],
                    "values": field.get("values", []),
                    "response": True
                } 
                for field in rules_data.get("form_fields", [])
                if field["field_type"] == "TERMS"
            ]
        }
    
    @classmethod
    def server_rules(cls, token: str, guild_id: str) -> bool:
        """Full workflow to accept server rules"""
        rules = cls.fetch_server_rules(token, guild_id)
        if not rules:
            return False
    
        payload = cls.generate_rule_response(rules)
        
        payload["additional_metadata"] = {
            "nonce": f"{random.randint(1000, 9999)}:{int(time.time() * 1000)}",
            "timestamp": datetime.now().isoformat()
        }
    
        endpoint = f"{cls.BASE_URL}/guilds/{guild_id}/requests/@me"
        header_generator = HeaderGenerator()
        headers = header_generator.generate_headers(token)
    
        try:
            response = requests.put(
                endpoint,
                headers=headers,
                json=payload,
                impersonate=header_generator.impersonate_target
            )
            if response.status_code in (200, 201, 204):
                logger.success("Successfully bypassed server rules!")
                return True
            logger.error(f"Rules bypass failed: {response.status_code} - {response.text}")
            return False
        except Exception as e:
            logger.error(f"Rules submission error: {e}")
            return False