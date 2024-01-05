from .models import ReferralLink


async def create_referral_link(name: str) -> ReferralLink:
    link, created = await ReferralLink.get_or_create(name=name)
    return link


async def get_all_links() -> list[ReferralLink]:
    return await ReferralLink.all()


async def is_link_exists(name: str) -> bool:
    return await ReferralLink.filter(name=name).exists()


async def increase_users_count(name: str):
    link: ReferralLink = await ReferralLink.get_or_none(name=name)
    if link:
        link.user_count += 1
        await link.save()


async def delete_link(link_id: int):
    link: ReferralLink = await ReferralLink.get_or_none(id=link_id)

    if not link:
        return

    await link.delete()
