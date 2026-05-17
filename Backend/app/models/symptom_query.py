"""
SymptomQuery SQLAlchemy Model.

Stores each symptom analysis performed by a user, creating
a personal health history log. Anonymous queries are not stored.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class SymptomQuery(Base):
    __tablename__ = "symptom_queries"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    symptoms_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    diagnosis: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
    )
    severity: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    source: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Relationship back to User
    user = relationship("User", backref="symptom_queries")

    def __repr__(self) -> str:
        return f"<SymptomQuery id={self.id} user_id={self.user_id} diagnosis={self.diagnosis}>"
