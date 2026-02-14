"""
Google Drive Access Manager Bot
Enhanced with VJ-FILTER-BOT patterns

Author: Enhanced Version
Version: 3.0.0 (VJ-Enhanced)
"""

import asyncio
import importlib
import logging
from pathlib import Path
from datetime import datetime, timedelta

from pyrogram import Client, idle
from pyrogram.errors import FloodWait

from config import Config
from services.database import Database
from services.drive import DriveService
from services.broadcast import BroadcastService
from utils.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)

class BotCore:
    """Enhanced Bot Core with VJ patterns"""
    
    def __init__(self):
        self.app = Client(
            "drive_access_bot",
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            bot_token=Config.BOT_TOKEN,
            plugins=dict(root="plugins")
        )
        
        self.db = Database()
        self.drive = DriveService()
        self.broadcast = BroadcastService()
        
        self.plugins = {}
        self.start_time = datetime.utcnow()
        
    async def initialize(self):
        """Initialize bot services"""
        try:
            logger.info("🚀 Initializing bot services...")
            
            # Initialize database
            await self.db.connect()
            logger.info("✅ Database connected")
            
            # Initialize Drive service
            await self.drive.initialize()
            logger.info("✅ Drive service initialized")
            
            # Load plugins
            self.load_plugins()
            logger.info(f"✅ Loaded {len(self.plugins)} plugins")
            
            # Start auto-expire scheduler
            asyncio.create_task(self.auto_expire_scheduler())
            logger.info("✅ Auto-expire scheduler started")
            
            logger.info("✨ Bot initialization complete!")
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}", exc_info=True)
            raise
    
    def load_plugins(self):
        """Dynamic plugin loader (VJ pattern)"""
        plugin_dir = Path("plugins")
        
        if not plugin_dir.exists():
            logger.warning("Plugins directory not found!")
            return
        
        for plugin_file in sorted(plugin_dir.glob("*.py")):
            # Skip private modules
            if plugin_file.name.startswith("_"):
                continue
            
            module_name = f"plugins.{plugin_file.stem}"
            
            try:
                module = importlib.import_module(module_name)
                self.plugins[plugin_file.stem] = module
                logger.info(f"  ✓ Loaded: {plugin_file.stem}")
                
            except Exception as e:
                logger.error(f"  ✗ Failed to load {plugin_file.stem}: {e}")
    
    async def reload_plugin(self, plugin_name: str) -> bool:
        """Hot reload a plugin (VJ feature)"""
        module_name = f"plugins.{plugin_name}"
        
        try:
            module = importlib.reload(
                importlib.import_module(module_name)
            )
            self.plugins[plugin_name] = module
            logger.info(f"✅ Reloaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to reload {plugin_name}: {e}")
            return False
    
    async def auto_expire_scheduler(self):
        """Background task to auto-revoke expired grants"""
        logger.info("⏰ Auto-expire scheduler started")
        
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                # Get expired grants
                expired_grants = await self.db.get_expired_grants()
                
                if not expired_grants:
                    continue
                
                logger.info(f"🔍 Found {len(expired_grants)} expired grants")
                
                for grant in expired_grants:
                    try:
                        # Revoke access
                        await self.drive.remove_permission(
                            folder_id=grant['folder_id'],
                            permission_id=grant['permission_id']
                        )
                        
                        # Update database
                        await self.db.mark_grant_revoked(
                            grant_id=grant['_id'],
                            revoke_type='auto_revoke'
                        )
                        
                        # Log activity
                        await self.db.add_log({
                            'type': 'auto_revoke',
                            'email': grant['email'],
                            'folder_id': grant['folder_id'],
                            'folder_name': grant.get('folder_name', 'Unknown'),
                            'reason': 'Expired',
                            'timestamp': datetime.utcnow()
                        })
                        
                        # Broadcast notification
                        if Config.AUTO_EXPIRE_NOTIFICATIONS:
                            await self.broadcast.send_expiry_notification(grant)
                        
                        logger.info(f"✅ Auto-revoked: {grant['email']} from {grant['folder_name']}")
                        
                    except Exception as e:
                        logger.error(f"❌ Failed to revoke {grant['email']}: {e}")
                        continue
                
                logger.info(f"✨ Auto-expire cycle complete: {len(expired_grants)} processed")
                
            except Exception as e:
                logger.error(f"❌ Auto-expire scheduler error: {e}", exc_info=True)
                await asyncio.sleep(60)  # Wait 1 minute before retry
    
    async def start(self):
        """Start the bot"""
        try:
            await self.initialize()
            await self.app.start()
            
            # Get bot info
            me = await self.app.get_me()
            logger.info(f"""
╔════════════════════════════════════════════╗
║  🤖 Bot Started Successfully!              ║
╠════════════════════════════════════════════╣
║  Name     : {me.first_name:<30} ║
║  Username : @{me.username:<29} ║
║  ID       : {me.id:<30} ║
║  Version  : v3.0.0 (VJ-Enhanced)          ║
╚════════════════════════════════════════════╝
            """)
            
            # Send startup notification to admins
            await self.broadcast.notify_admins(
                "✅ **Bot Started Successfully!**\n\n"
                f"🤖 **{me.first_name}** (@{me.username})\n"
                f"🆔 ID: `{me.id}`\n"
                f"🔄 Version: v3.0.0\n"
                f"⏰ Started: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
            )
            
            await idle()
            
        except KeyboardInterrupt:
            logger.info("🛑 Bot stopped by user")
        except Exception as e:
            logger.error(f"❌ Bot crashed: {e}", exc_info=True)
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the bot gracefully"""
        logger.info("🛑 Stopping bot...")
        
        try:
            await self.app.stop()
            await self.db.close()
            logger.info("✅ Bot stopped successfully")
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")

# Main execution
if __name__ == "__main__":
    bot = BotCore()
    asyncio.run(bot.start())
