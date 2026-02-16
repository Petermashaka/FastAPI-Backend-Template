async def update_account_by_id(self, id: int, account_update: AccountInUpdate) -> Account:
    new_account_data = account_update.dict(exclude_unset=True)

    # Fetch the account
    select_stmt = sqlalchemy.select(Account).where(Account.id == id)
    query = await self.async_session.execute(statement=select_stmt)
    update_account = query.scalar()

    if not update_account:
        raise EntityDoesNotExist(f"Account with id `{id}` does not exist!")  # type: ignore

    # Start building the update statement
    update_stmt = sqlalchemy.update(Account).where(Account.id == update_account.id).values(
        updated_at=sqlalchemy_functions.now()
    )

    # Update fields if provided
    if new_account_data.get("username"):
        update_stmt = update_stmt.values(username=new_account_data["username"])

    if new_account_data.get("email"):
        update_stmt = update_stmt.values(email=new_account_data["email"])  # Fixed previous bug

    if new_account_data.get("password"):
        # Efficiently generate new salt and hashed password
        new_salt = pwd_generator.generate_salt()
        new_hashed_password = pwd_generator.generate_hashed_password(
            hash_salt=new_salt, new_password=new_account_data["password"]
        )
        update_stmt = update_stmt.values(
            hash_salt=new_salt,
            hashed_password=new_hashed_password
        )

    # Execute the update
    await self.async_session.execute(statement=update_stmt)
    await self.async_session.commit()

    # Refresh the object to reflect updated values
    await self.async_session.refresh(instance=update_account)

    return update_account  # type: ignore
