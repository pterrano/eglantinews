class EglantineConfig:

    def get_rooms_config(self) -> dict:
        return {
            "LIVING": {
                "hostname": "amplifier",
                "label": "le salon",
                "default-volume": 60,
                "max-volume": 120,
                "default": True
            },

            "DESKTOP": {
                "hostname": "wx051",
                "label": "le bureau",
                "default-volume": 50
            }
        }

    def get_authorised_users(self):
        return [
            '...'
        ]

    def get_authorised_devices(self):
        return [
            '...'
        ]

    def get_ws_infos(self):
        return {
            'name': 'Eglantine Skill WebService',
            'id': 'eglantine-skill',
            'version': '1.0'
        }

    def get_multiroom_link_group_id(self) -> str:
        return "d9ded9c3eea94ba8b137a805dc6d8942"

    def get_multiroom_link_group_name(self) -> str:
        return "EglantineGroup"
