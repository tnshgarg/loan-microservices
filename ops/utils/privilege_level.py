from dal.models.sales_users import SalesUser

SALES_USER_PRIVILEGE_MAP = {
    SalesUser.Type.SM: 0,
    SalesUser.Type.RM: 1,
    SalesUser.Type.MANAGER: 2,
    SalesUser.Type.ADMIN: 3
}


def is_sales_user_privileged(email):
    # fetch sales user details
    sales_user_info = SalesUser.find_one({"email": email})
    sales_user_type = sales_user_info.get("type", SalesUser.Type.SM)
    sales_user_privilege = SALES_USER_PRIVILEGE_MAP.get(sales_user_type, 0)

    return sales_user_privilege >= 2
