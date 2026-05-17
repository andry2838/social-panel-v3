from sqlalchemy import Column, Integer, String, Boolean, JSON, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class Account(Base):
    __tablename__ = "accounts"
    
    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    platform = Column(String, default="instagram")
    proxy = Column(String, nullable=True)
    status = Column(String, default="active")
    tags = Column(JSON, default=[])
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Unified new fields
    two_factor_seed = Column(String, nullable=True)
    email = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    last_action = Column(DateTime, nullable=True)
    daily_actions = Column(Integer, default=0)
    total_actions = Column(Integer, default=0)
    notes = Column(String, nullable=True)
    
    # Relations
    campaigns = relationship("Campaign", back_populates="account")
    logs = relationship("ActionLog", back_populates="account")

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(String, primary_key=True)
    account_id = Column(String, ForeignKey("accounts.id"))
    name = Column(String)
    type = Column(String) # SMART ou EXPERT
    
    # Configuration avancée
    targets = Column(JSON, default={}) # {"competitors": [], "hashtags": [], "locations": []}
    features = Column(JSON, default={}) # {"story_polls": true, "mass_look": true, "auto_like_feed": true}
    
    # IA et Filtres
    ai_settings = Column(JSON, default={}) # {"provider": "groq", "spintax": "...", "lang_filter": ["fr", "mg"]}
    
    # Gestionnaire de Temps (Activity Settings)
    activity_settings = Column(JSON, default={}) # {"sleep_night": true, "min_delay": 5, "max_delay": 30}
    
    status = Column(String, default="paused")
    
    # Relations
    account = relationship("Account", back_populates="campaigns")
    logs = relationship("ActionLog", back_populates="campaign")

class ActionLog(Base):
    __tablename__ = "action_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    account_id = Column(String, ForeignKey("accounts.id"))
    campaign_id = Column(String, ForeignKey("campaigns.id"), nullable=True)
    
    action_type = Column(String) # ex: story_poll_vote, like_comment, unfollow
    target_user = Column(String)
    source = Column(String, nullable=True) # Pour le Source Tracking
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relations
    account = relationship("Account", back_populates="logs")
    campaign = relationship("Campaign", back_populates="logs")

class SourceTracking(Base):
    __tablename__ = "source_tracking"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    campaign_id = Column(String, ForeignKey("campaigns.id"))
    source_name = Column(String) # Le nom du concurrent ou hashtag
    conversion_type = Column(String) # "new_follower", "like_back", etc.
    count = Column(Integer, default=1)
