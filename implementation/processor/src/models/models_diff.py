"""
ApiKey model changes for OAuth Codex support.

Apply these changes to: evo-ai-processor-community/src/models/models.py

DIFF — Replace the ApiKey class with:
"""


# --- BEFORE (original) ---
# class ApiKey(Base):
#     __tablename__ = "api_keys"
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"))
#     name = Column(String, nullable=False)
#     provider = Column(String, nullable=False)
#     encrypted_key = Column(String, nullable=False)    <-- WAS NOT NULL
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     updated_at = Column(DateTime(timezone=True), onupdate=func.now())
#     is_active = Column(Boolean, default=True)
#     client = relationship("Client", backref="api_keys")


# --- AFTER (with OAuth Codex) ---
# class ApiKey(Base):
#     __tablename__ = "api_keys"
#     id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
#     client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id", ondelete="CASCADE"))
#     name = Column(String, nullable=False)
#     provider = Column(String, nullable=False)
#     encrypted_key = Column(String, nullable=True)                            <-- NOW NULLABLE
#     auth_type = Column(String(20), nullable=False, server_default="api_key") <-- NEW
#     oauth_data = Column(Text, nullable=True)                                 <-- NEW
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     updated_at = Column(DateTime(timezone=True), onupdate=func.now())
#     is_active = Column(Boolean, default=True)
#     client = relationship("Client", backref="api_keys")


# Changes summary:
# 1. encrypted_key: nullable=False -> nullable=True
# 2. NEW: auth_type = Column(String(20), nullable=False, server_default="api_key")
# 3. NEW: oauth_data = Column(Text, nullable=True)
