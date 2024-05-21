# from sqlalchemy import BigInteger, VARCHAR
# from sqlalchemy.orm import mapped_column, Mapped
#
# from db.base import CreatedModel
#
#
# class User(CreatedModel):
#     id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
#     first_name: Mapped[str] = mapped_column(VARCHAR(255))
#     last_name: Mapped[str] = mapped_column(VARCHAR(255), nullable=True)
#     email: Mapped[str] = mapped_column(VARCHAR(255), unique=True, nullable=True)
#     password: Mapped[str] = mapped_column(VARCHAR(255), nullable=True)
#
#     username: Mapped[str] = mapped_column(VARCHAR(255), nullable=True)
#     phone_number: Mapped[str] = mapped_column(VARCHAR(255), nullable=True)
