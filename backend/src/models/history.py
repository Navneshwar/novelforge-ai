from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.core.database import Base


class GenerationHistory(Base):
    __tablename__ = "generation_history"
    
    id = Column(Integer, primary_key=True, index=True)
    novel_id = Column(Integer, ForeignKey("novels.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    prompt = Column(Text, nullable=False)
    context = Column(Text, nullable=True)
    generated_text = Column(Text, nullable=False)
    style = Column(String(100), default="continue")
    model = Column(String(255), nullable=True)
    temperature = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="generation_history")
