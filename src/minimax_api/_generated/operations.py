"""Operations generated from the Minimax Swagger document. Do not edit.

One function per Swagger operation. Names come from the operationId; where
several operations share one operationId, the path tail disambiguates them
(`customer_get`, `customer_get_by_customer_id`, `customer_get_by_code`).

Regenerate with `uv run python scripts/generate.py`.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from minimax_api._generated.models import (
    Account,
    AddressModel,
    Analytic,
    AnalyticSearch,
    Attachment,
    BankAccount,
    Contact,
    Country,
    Currency,
    Customer,
    CustomerSearch,
    Dashboard,
    Document,
    DocumentAttachment,
    DocumentNumbering,
    DocumentSearch,
    EFakturaEntry,
    Employee,
    EmployeeSearch,
    ExchangeRate,
    Inbox,
    InboxAttachment,
    IssuedInvoice,
    IssuedInvoicePaymentMethodSearch,
    IssuedInvoicePosting,
    IssuedInvoicePostingPaymentMethodSearch,
    IssuedInvoicePostingSearch,
    IssuedInvoiceSearch,
    Item,
    ItemDataListResult,
    ItemPriceListItemListResult,
    ItemSearch,
    ItemsSettings,
    Journal,
    JournalEntries,
    JournalSearch,
    JournalType,
    Order,
    OrderSearch,
    Organisation,
    Outbox,
    PaymentMethodPaymentMethodSearch,
    PayrollSettings,
    PostalCode,
    ProductGroup,
    PurposeCode,
    ReceivedInvoice,
    ReceivedInvoiceSearch,
    ReportTemplate,
    StockEntry,
    StockEntrySearch,
    StockListItem,
    SyncQueryResult,
    User,
    UserOrganisation,
    VatAccountingType,
    VATEntry,
    VatRate,
    Warehouse,
)
from minimax_api.envelope import SearchResult
from minimax_api.transport import Transport


def account_get(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[Account]:
    """`GET /api/orgs/{organisationId}/accounts` (operationId `Account_Get`)."""
    response = transport.request("GET", f"/api/orgs/{organisation_id}/accounts", params=params)
    return SearchResult[Account].model_validate(response.json)


def account_get_by_account_id(
    transport: Transport,
    *,
    organisation_id: int,
    account_id: int,
    params: Mapping[str, Any] | None = None,
) -> Account:
    """`GET /api/orgs/{organisationId}/accounts/{accountId}` (operationId `Account_Get`)."""
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/accounts/{account_id}",
        params=params,
    )
    return Account.model_validate(response.json)


def account_get_by_code(
    transport: Transport,
    *,
    organisation_id: int,
    code: str,
    params: Mapping[str, Any] | None = None,
) -> Account:
    """`GET /api/orgs/{organisationId}/accounts/code({code})` (operationId `Account_Get`)."""
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/accounts/code({code})",
        params=params,
    )
    return Account.model_validate(response.json)


def account_get_by_content(
    transport: Transport,
    *,
    organisation_id: int,
    content: str,
    params: Mapping[str, Any] | None = None,
) -> Account:
    """`GET /api/orgs/{organisationId}/accounts/content({content})` (operationId
    `Account_GetByContent`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/accounts/content({content})",
        params=params,
    )
    return Account.model_validate(response.json)


def account_get_accounts_sync_candidates(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SyncQueryResult:
    """`GET /api/orgs/{organisationId}/accounts/synccandidates` (operationId
    `Account_GetAccountsSyncCandidates`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/accounts/synccandidates",
        params=params,
    )
    return SyncQueryResult.model_validate(response.json)


def address_get_by_customer_id_addresses(
    transport: Transport,
    *,
    organisation_id: int,
    customer_id: int,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[AddressModel]:
    """`GET /api/orgs/{organisationId}/customers/{customerId}/addresses` (operationId
    `Address_Get`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/customers/{customer_id}/addresses",
        params=params,
    )
    return SearchResult[AddressModel].model_validate(response.json)


def address_post_by_customer_id_addresses(
    transport: Transport,
    *,
    organisation_id: int,
    customer_id: int,
    body: AddressModel,
) -> int | None:
    """`POST /api/orgs/{organisationId}/customers/{customerId}/addresses` (operationId
    `Address_Post`).
    """
    response = transport.request(
        "POST",
        f"/api/orgs/{organisation_id}/customers/{customer_id}/addresses",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return response.location_id


def address_get_by_customer_id_addresses_by_address_id(
    transport: Transport,
    *,
    organisation_id: int,
    customer_id: int,
    address_id: int,
    params: Mapping[str, Any] | None = None,
) -> AddressModel:
    """`GET /api/orgs/{organisationId}/customers/{customerId}/addresses/{addressId}` (operationId
    `Address_Get`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/customers/{customer_id}/addresses/{address_id}",
        params=params,
    )
    return AddressModel.model_validate(response.json)


def address_put_by_customer_id_addresses_by_address_id(
    transport: Transport,
    *,
    organisation_id: int,
    customer_id: int,
    address_id: int,
    body: AddressModel,
) -> None:
    """`PUT /api/orgs/{organisationId}/customers/{customerId}/addresses/{addressId}` (operationId
    `Address_Put`).
    """
    transport.request(
        "PUT",
        f"/api/orgs/{organisation_id}/customers/{customer_id}/addresses/{address_id}",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return None


def address_delete_by_customer_id_addresses_by_address_id(
    transport: Transport,
    *,
    organisation_id: int,
    customer_id: int,
    address_id: int,
) -> None:
    """`DELETE /api/orgs/{organisationId}/customers/{customerId}/addresses/{addressId}` (operationId
    `Address_Delete`).
    """
    transport.request(
        "DELETE",
        f"/api/orgs/{organisation_id}/customers/{customer_id}/addresses/{address_id}",
    )
    return None


def address_get_addresses_sync_candidates(
    transport: Transport,
    *,
    organisation_id: int,
    customer_id: str,
    params: Mapping[str, Any] | None = None,
) -> SyncQueryResult:
    """`GET /api/orgs/{organisationId}/customers/{customerId}/addresses/synccandidates` (operationId
    `Address_GetAddressesSyncCandidates`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/customers/{customer_id}/addresses/synccandidates",
        params=params,
    )
    return SyncQueryResult.model_validate(response.json)


def analytic_get(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[AnalyticSearch]:
    """`GET /api/orgs/{organisationId}/analytics` (operationId `Analytic_Get`)."""
    response = transport.request("GET", f"/api/orgs/{organisation_id}/analytics", params=params)
    return SearchResult[AnalyticSearch].model_validate(response.json)


def analytic_post(
    transport: Transport,
    *,
    organisation_id: int,
    body: Analytic,
) -> int | None:
    """`POST /api/orgs/{organisationId}/analytics` (operationId `Analytic_Post`)."""
    response = transport.request(
        "POST",
        f"/api/orgs/{organisation_id}/analytics",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return response.location_id


def analytic_get_by_analytic_id(
    transport: Transport,
    *,
    organisation_id: int,
    analytic_id: int,
    params: Mapping[str, Any] | None = None,
) -> Analytic:
    """`GET /api/orgs/{organisationId}/analytics/{analyticId}` (operationId `Analytic_Get`)."""
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/analytics/{analytic_id}",
        params=params,
    )
    return Analytic.model_validate(response.json)


def analytic_put_by_analytic_id(
    transport: Transport,
    *,
    organisation_id: int,
    analytic_id: int,
    body: Analytic,
) -> None:
    """`PUT /api/orgs/{organisationId}/analytics/{analyticId}` (operationId `Analytic_Put`)."""
    transport.request(
        "PUT",
        f"/api/orgs/{organisation_id}/analytics/{analytic_id}",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return None


def analytic_delete_by_analytic_id(
    transport: Transport,
    *,
    organisation_id: int,
    analytic_id: int,
) -> None:
    """`DELETE /api/orgs/{organisationId}/analytics/{analyticId}` (operationId `Analytic_Delete`).
    """
    transport.request("DELETE", f"/api/orgs/{organisation_id}/analytics/{analytic_id}")
    return None


def analytic_get_analytics_sync_candidates(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SyncQueryResult:
    """`GET /api/orgs/{organisationId}/analytics/synccandidates` (operationId
    `Analytic_GetAnalyticsSyncCandidates`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/analytics/synccandidates",
        params=params,
    )
    return SyncQueryResult.model_validate(response.json)


def bank_account_get_by_customer_id_bank_accounts(
    transport: Transport,
    *,
    organisation_id: int,
    customer_id: int,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[BankAccount]:
    """`GET /api/orgs/{organisationId}/customers/{customerId}/bankAccounts` (operationId
    `BankAccount_Get`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/customers/{customer_id}/bankAccounts",
        params=params,
    )
    return SearchResult[BankAccount].model_validate(response.json)


def bank_account_post_by_customer_id_bank_accounts(
    transport: Transport,
    *,
    organisation_id: int,
    customer_id: int,
    body: BankAccount,
) -> int | None:
    """`POST /api/orgs/{organisationId}/customers/{customerId}/bankAccounts` (operationId
    `BankAccount_Post`).
    """
    response = transport.request(
        "POST",
        f"/api/orgs/{organisation_id}/customers/{customer_id}/bankAccounts",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return response.location_id


def bank_account_get_by_customer_id_bank_accounts_by_bank_account_id(
    transport: Transport,
    *,
    organisation_id: int,
    customer_id: int,
    bank_account_id: int,
    params: Mapping[str, Any] | None = None,
) -> BankAccount:
    """`GET /api/orgs/{organisationId}/customers/{customerId}/bankAccounts/{bankAccountId}`
    (operationId `BankAccount_Get`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/customers/{customer_id}/bankAccounts/{bank_account_id}",
        params=params,
    )
    return BankAccount.model_validate(response.json)


def bank_account_put_by_customer_id_bank_accounts_by_bank_account_id(
    transport: Transport,
    *,
    organisation_id: int,
    customer_id: int,
    bank_account_id: int,
    body: BankAccount,
) -> None:
    """`PUT /api/orgs/{organisationId}/customers/{customerId}/bankAccounts/{bankAccountId}`
    (operationId `BankAccount_Put`).
    """
    transport.request(
        "PUT",
        f"/api/orgs/{organisation_id}/customers/{customer_id}/bankAccounts/{bank_account_id}",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return None


def bank_account_delete_by_customer_id_bank_accounts_by_bank_account_id(
    transport: Transport,
    *,
    organisation_id: int,
    customer_id: int,
    bank_account_id: int,
) -> None:
    """`DELETE /api/orgs/{organisationId}/customers/{customerId}/bankAccounts/{bankAccountId}`
    (operationId `BankAccount_Delete`).
    """
    transport.request(
        "DELETE",
        f"/api/orgs/{organisation_id}/customers/{customer_id}/bankAccounts/{bank_account_id}",
    )
    return None


def bank_account_get_bank_accounts_sync_candidates(
    transport: Transport,
    *,
    organisation_id: int,
    customer_id: str,
    params: Mapping[str, Any] | None = None,
) -> SyncQueryResult:
    """`GET /api/orgs/{organisationId}/customers/{customerId}/bankAccounts/synccandidates`
    (operationId `BankAccount_GetBankAccountsSyncCandidates`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/customers/{customer_id}/bankAccounts/synccandidates",
        params=params,
    )
    return SyncQueryResult.model_validate(response.json)


def contact_get_by_customer_id_contacts(
    transport: Transport,
    *,
    organisation_id: int,
    customer_id: int,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[Contact]:
    """`GET /api/orgs/{organisationId}/customers/{customerId}/contacts` (operationId `Contact_Get`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/customers/{customer_id}/contacts",
        params=params,
    )
    return SearchResult[Contact].model_validate(response.json)


def contact_post_by_customer_id_contacts(
    transport: Transport,
    *,
    organisation_id: int,
    customer_id: int,
    body: Contact,
) -> int | None:
    """`POST /api/orgs/{organisationId}/customers/{customerId}/contacts` (operationId
    `Contact_Post`).
    """
    response = transport.request(
        "POST",
        f"/api/orgs/{organisation_id}/customers/{customer_id}/contacts",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return response.location_id


def contact_get_by_customer_id_contacts_by_contact_id(
    transport: Transport,
    *,
    organisation_id: int,
    customer_id: int,
    contact_id: int,
    params: Mapping[str, Any] | None = None,
) -> Contact:
    """`GET /api/orgs/{organisationId}/customers/{customerId}/contacts/{contactId}` (operationId
    `Contact_Get`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/customers/{customer_id}/contacts/{contact_id}",
        params=params,
    )
    return Contact.model_validate(response.json)


def contact_put_by_customer_id_contacts_by_contact_id(
    transport: Transport,
    *,
    organisation_id: int,
    customer_id: int,
    contact_id: int,
    body: Contact,
) -> None:
    """`PUT /api/orgs/{organisationId}/customers/{customerId}/contacts/{contactId}` (operationId
    `Contact_Put`).
    """
    transport.request(
        "PUT",
        f"/api/orgs/{organisation_id}/customers/{customer_id}/contacts/{contact_id}",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return None


def contact_delete_by_customer_id_contacts_by_contact_id(
    transport: Transport,
    *,
    organisation_id: int,
    customer_id: int,
    contact_id: int,
) -> None:
    """`DELETE /api/orgs/{organisationId}/customers/{customerId}/contacts/{contactId}` (operationId
    `Contact_Delete`).
    """
    transport.request(
        "DELETE",
        f"/api/orgs/{organisation_id}/customers/{customer_id}/contacts/{contact_id}",
    )
    return None


def contact_get_contacts(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[Contact]:
    """`GET /api/orgs/{organisationId}/contacts` (operationId `Contact_GetContacts`)."""
    response = transport.request("GET", f"/api/orgs/{organisation_id}/contacts", params=params)
    return SearchResult[Contact].model_validate(response.json)


def contact_get_contacts_sync_candidates(
    transport: Transport,
    *,
    organisation_id: int,
    customer_id: str,
    params: Mapping[str, Any] | None = None,
) -> SyncQueryResult:
    """`GET /api/orgs/{organisationId}/customers/{customerId}/contacts/synccandidates` (operationId
    `Contact_GetContactsSyncCandidates`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/customers/{customer_id}/contacts/synccandidates",
        params=params,
    )
    return SyncQueryResult.model_validate(response.json)


def country_get(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[Country]:
    """`GET /api/orgs/{organisationId}/countries` (operationId `Country_Get`)."""
    response = transport.request("GET", f"/api/orgs/{organisation_id}/countries", params=params)
    return SearchResult[Country].model_validate(response.json)


def country_get_by_country_id(
    transport: Transport,
    *,
    organisation_id: int,
    country_id: int,
    params: Mapping[str, Any] | None = None,
) -> Country:
    """`GET /api/orgs/{organisationId}/countries/{countryId}` (operationId `Country_Get`)."""
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/countries/{country_id}",
        params=params,
    )
    return Country.model_validate(response.json)


def country_get_by_code(
    transport: Transport,
    *,
    organisation_id: int,
    code: str,
    params: Mapping[str, Any] | None = None,
) -> Country:
    """`GET /api/orgs/{organisationId}/countries/code({code})` (operationId `Country_Get`)."""
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/countries/code({code})",
        params=params,
    )
    return Country.model_validate(response.json)


def country_get_countries_sync_candidates(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SyncQueryResult:
    """`GET /api/orgs/{organisationId}/countries/synccandidates` (operationId
    `Country_GetCountriesSyncCandidates`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/countries/synccandidates",
        params=params,
    )
    return SyncQueryResult.model_validate(response.json)


def currency_get(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[Currency]:
    """`GET /api/orgs/{organisationId}/currencies` (operationId `Currency_Get`)."""
    response = transport.request("GET", f"/api/orgs/{organisation_id}/currencies", params=params)
    return SearchResult[Currency].model_validate(response.json)


def currency_get_by_currency_id(
    transport: Transport,
    *,
    organisation_id: int,
    currency_id: int,
    params: Mapping[str, Any] | None = None,
) -> Currency:
    """`GET /api/orgs/{organisationId}/currencies/{currencyId}` (operationId `Currency_Get`)."""
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/currencies/{currency_id}",
        params=params,
    )
    return Currency.model_validate(response.json)


def currency_get_by_date(
    transport: Transport,
    *,
    organisation_id: int,
    date: str,
    params: Mapping[str, Any] | None = None,
) -> Currency:
    """`GET /api/orgs/{organisationId}/currencies/date({date})` (operationId `Currency_Get`)."""
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/currencies/date({date})",
        params=params,
    )
    return Currency.model_validate(response.json)


def currency_get_by_code(
    transport: Transport,
    *,
    organisation_id: int,
    code: str,
    params: Mapping[str, Any] | None = None,
) -> Currency:
    """`GET /api/orgs/{organisationId}/currencies/code({code})` (operationId `Currency_Get`)."""
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/currencies/code({code})",
        params=params,
    )
    return Currency.model_validate(response.json)


def currency_get_currencies_sync_candidates(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SyncQueryResult:
    """`GET /api/orgs/{organisationId}/currencies/synccandidates` (operationId
    `Currency_GetCurrenciesSyncCandidates`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/currencies/synccandidates",
        params=params,
    )
    return SyncQueryResult.model_validate(response.json)


def customer_get(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[CustomerSearch]:
    """`GET /api/orgs/{organisationId}/customers` (operationId `Customer_Get`)."""
    response = transport.request("GET", f"/api/orgs/{organisation_id}/customers", params=params)
    return SearchResult[CustomerSearch].model_validate(response.json)


def customer_post(
    transport: Transport,
    *,
    organisation_id: int,
    body: Customer,
) -> int | None:
    """`POST /api/orgs/{organisationId}/customers` (operationId `Customer_Post`)."""
    response = transport.request(
        "POST",
        f"/api/orgs/{organisation_id}/customers",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return response.location_id


def customer_get_by_customer_id(
    transport: Transport,
    *,
    organisation_id: int,
    customer_id: int,
    params: Mapping[str, Any] | None = None,
) -> Customer:
    """`GET /api/orgs/{organisationId}/customers/{customerId}` (operationId `Customer_Get`)."""
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/customers/{customer_id}",
        params=params,
    )
    return Customer.model_validate(response.json)


def customer_put_by_customer_id(
    transport: Transport,
    *,
    organisation_id: int,
    customer_id: int,
    body: Customer,
) -> None:
    """`PUT /api/orgs/{organisationId}/customers/{customerId}` (operationId `Customer_Put`)."""
    transport.request(
        "PUT",
        f"/api/orgs/{organisation_id}/customers/{customer_id}",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return None


def customer_delete_by_customer_id(
    transport: Transport,
    *,
    organisation_id: int,
    customer_id: int,
) -> None:
    """`DELETE /api/orgs/{organisationId}/customers/{customerId}` (operationId `Customer_Delete`).
    """
    transport.request("DELETE", f"/api/orgs/{organisation_id}/customers/{customer_id}")
    return None


def customer_get_by_code(
    transport: Transport,
    *,
    organisation_id: int,
    code: str,
    params: Mapping[str, Any] | None = None,
) -> Customer:
    """`GET /api/orgs/{organisationId}/customers/code({code})` (operationId `Customer_Get`)."""
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/customers/code({code})",
        params=params,
    )
    return Customer.model_validate(response.json)


def customer_add_customer_by_tax_number(
    transport: Transport,
    *,
    organisation_id: int,
    tax_number: str,
) -> int | None:
    """`POST /api/orgs/{organisationId}/customers/addbytaxnumber({taxNumber})` (operationId
    `Customer_AddCustomerByTaxNumber`).
    """
    response = transport.request(
        "POST",
        f"/api/orgs/{organisation_id}/customers/addbytaxnumber({tax_number})",
    )
    return response.location_id


def customer_get_customers_sync_candidates(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SyncQueryResult:
    """`GET /api/orgs/{organisationId}/customers/synccandidates` (operationId
    `Customer_GetCustomersSyncCandidates`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/customers/synccandidates",
        params=params,
    )
    return SyncQueryResult.model_validate(response.json)


def dashboard_get(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> Dashboard:
    """`GET /api/orgs/{organisationId}/dashboards` (operationId `Dashboard_Get`)."""
    response = transport.request("GET", f"/api/orgs/{organisation_id}/dashboards", params=params)
    return Dashboard.model_validate(response.json)


def document_get(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[DocumentSearch]:
    """`GET /api/orgs/{organisationId}/documents` (operationId `Document_Get`)."""
    response = transport.request("GET", f"/api/orgs/{organisation_id}/documents", params=params)
    return SearchResult[DocumentSearch].model_validate(response.json)


def document_post(
    transport: Transport,
    *,
    organisation_id: int,
    body: Document,
) -> int | None:
    """`POST /api/orgs/{organisationId}/documents` (operationId `Document_Post`)."""
    response = transport.request(
        "POST",
        f"/api/orgs/{organisation_id}/documents",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return response.location_id


def document_get_by_document_id(
    transport: Transport,
    *,
    organisation_id: int,
    document_id: int,
    params: Mapping[str, Any] | None = None,
) -> Document:
    """`GET /api/orgs/{organisationId}/documents/{documentId}` (operationId `Document_Get`)."""
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/documents/{document_id}",
        params=params,
    )
    return Document.model_validate(response.json)


def document_put_by_document_id(
    transport: Transport,
    *,
    organisation_id: int,
    document_id: int,
    body: Document,
) -> None:
    """`PUT /api/orgs/{organisationId}/documents/{documentId}` (operationId `Document_Put`)."""
    transport.request(
        "PUT",
        f"/api/orgs/{organisation_id}/documents/{document_id}",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return None


def document_delete_by_document_id(
    transport: Transport,
    *,
    organisation_id: int,
    document_id: int,
) -> None:
    """`DELETE /api/orgs/{organisationId}/documents/{documentId}` (operationId `Document_Delete`).
    """
    transport.request("DELETE", f"/api/orgs/{organisation_id}/documents/{document_id}")
    return None


def document_get_document_attachment_by_document_id_attachments_by_document_attachment_id(
    transport: Transport,
    *,
    organisation_id: int,
    document_id: int,
    document_attachment_id: int,
    params: Mapping[str, Any] | None = None,
) -> DocumentAttachment:
    """`GET /api/orgs/{organisationId}/documents/{documentId}/attachments/{documentAttachmentId}`
    (operationId `Document_GetDocumentAttachment`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/documents/{document_id}/attachments/{document_attachment_id}",
        params=params,
    )
    return DocumentAttachment.model_validate(response.json)


def document_put_by_document_id_attachments_by_document_attachment_id(
    transport: Transport,
    *,
    organisation_id: int,
    document_id: int,
    document_attachment_id: int,
    body: DocumentAttachment,
) -> None:
    """`PUT /api/orgs/{organisationId}/documents/{documentId}/attachments/{documentAttachmentId}`
    (operationId `Document_Put`).
    """
    transport.request(
        "PUT",
        f"/api/orgs/{organisation_id}/documents/{document_id}/attachments/{document_attachment_id}",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return None


def document_delete_by_document_id_attachments_by_document_attachment_id(
    transport: Transport,
    *,
    organisation_id: int,
    document_id: int,
    document_attachment_id: int,
) -> None:
    """`DELETE /api/orgs/{organisationId}/documents/{documentId}/attachments/{documentAttachmentId}`
    (operationId `Document_Delete`).
    """
    transport.request(
        "DELETE",
        f"/api/orgs/{organisation_id}/documents/{document_id}/attachments/{document_attachment_id}",
    )
    return None


def document_post_document_attachment(
    transport: Transport,
    *,
    organisation_id: int,
    document_id: int,
    body: DocumentAttachment,
) -> int | None:
    """`POST /api/orgs/{organisationId}/documents/{documentId}/attachments` (operationId
    `Document_PostDocumentAttachment`).
    """
    response = transport.request(
        "POST",
        f"/api/orgs/{organisation_id}/documents/{document_id}/attachments",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return response.location_id


def document_get_documents_sync_candidates(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SyncQueryResult:
    """`GET /api/orgs/{organisationId}/documents/synccandidates` (operationId
    `Document_GetDocumentsSyncCandidates`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/documents/synccandidates",
        params=params,
    )
    return SyncQueryResult.model_validate(response.json)


def document_numbering_get(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[DocumentNumbering]:
    """`GET /api/orgs/{organisationId}/document-numbering` (operationId `DocumentNumbering_Get`)."""
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/document-numbering",
        params=params,
    )
    return SearchResult[DocumentNumbering].model_validate(response.json)


def document_numbering_get_by_document_numbering_id(
    transport: Transport,
    *,
    organisation_id: int,
    document_numbering_id: int,
    params: Mapping[str, Any] | None = None,
) -> DocumentNumbering:
    """`GET /api/orgs/{organisationId}/document-numbering/{documentNumberingId}` (operationId
    `DocumentNumbering_Get`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/document-numbering/{document_numbering_id}",
        params=params,
    )
    return DocumentNumbering.model_validate(response.json)


def e_faktura_get(
    transport: Transport,
    *,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[EFakturaEntry]:
    """`GET /api/efaktura/list` (operationId `EFaktura_Get`)."""
    response = transport.request("GET", "/api/efaktura/list", params=params)
    return SearchResult[EFakturaEntry].model_validate(response.json)


def employee_get(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[EmployeeSearch]:
    """`GET /api/orgs/{organisationId}/employees` (operationId `Employee_Get`)."""
    response = transport.request("GET", f"/api/orgs/{organisation_id}/employees", params=params)
    return SearchResult[EmployeeSearch].model_validate(response.json)


def employee_post(
    transport: Transport,
    *,
    organisation_id: int,
    body: Employee,
) -> int | None:
    """`POST /api/orgs/{organisationId}/employees` (operationId `Employee_Post`)."""
    response = transport.request(
        "POST",
        f"/api/orgs/{organisation_id}/employees",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return response.location_id


def employee_get_by_employee_id(
    transport: Transport,
    *,
    organisation_id: int,
    employee_id: int,
    params: Mapping[str, Any] | None = None,
) -> Employee:
    """`GET /api/orgs/{organisationId}/employees/{employeeId}` (operationId `Employee_Get`)."""
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/employees/{employee_id}",
        params=params,
    )
    return Employee.model_validate(response.json)


def employee_put_by_employee_id(
    transport: Transport,
    *,
    organisation_id: int,
    employee_id: int,
    body: Employee,
) -> None:
    """`PUT /api/orgs/{organisationId}/employees/{employeeId}` (operationId `Employee_Put`)."""
    transport.request(
        "PUT",
        f"/api/orgs/{organisation_id}/employees/{employee_id}",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return None


def employee_delete_by_employee_id(
    transport: Transport,
    *,
    organisation_id: int,
    employee_id: int,
) -> None:
    """`DELETE /api/orgs/{organisationId}/employees/{employeeId}` (operationId `Employee_Delete`).
    """
    transport.request("DELETE", f"/api/orgs/{organisation_id}/employees/{employee_id}")
    return None


def employee_get_employees_sync_candidates(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SyncQueryResult:
    """`GET /api/orgs/{organisationId}/employees/synccandidates` (operationId
    `Employee_GetEmployeesSyncCandidates`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/employees/synccandidates",
        params=params,
    )
    return SyncQueryResult.model_validate(response.json)


def exchange_rate_get(
    transport: Transport,
    *,
    organisation_id: int,
    currency_id: int,
    params: Mapping[str, Any] | None = None,
) -> ExchangeRate:
    """`GET /api/orgs/{organisationId}/exchange-rates/{currencyId}` (operationId
    `ExchangeRate_Get`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/exchange-rates/{currency_id}",
        params=params,
    )
    return ExchangeRate.model_validate(response.json)


def exchange_rate_get_by_code(
    transport: Transport,
    *,
    organisation_id: int,
    currency_code: str,
    params: Mapping[str, Any] | None = None,
) -> ExchangeRate:
    """`GET /api/orgs/{organisationId}/exchange-rates/code({currencyCode})` (operationId
    `ExchangeRate_GetByCode`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/exchange-rates/code({currency_code})",
        params=params,
    )
    return ExchangeRate.model_validate(response.json)


def inbox_get(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[Inbox]:
    """`GET /api/orgs/{organisationId}/inbox` (operationId `Inbox_Get`)."""
    response = transport.request("GET", f"/api/orgs/{organisation_id}/inbox", params=params)
    return SearchResult[Inbox].model_validate(response.json)


def inbox_post(
    transport: Transport,
    *,
    organisation_id: int,
    body: Inbox,
) -> int | None:
    """`POST /api/orgs/{organisationId}/inbox` (operationId `Inbox_Post`)."""
    response = transport.request(
        "POST",
        f"/api/orgs/{organisation_id}/inbox",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return response.location_id


def inbox_get_by_inbox_id(
    transport: Transport,
    *,
    organisation_id: int,
    inbox_id: int,
    params: Mapping[str, Any] | None = None,
) -> Inbox:
    """`GET /api/orgs/{organisationId}/inbox/{inboxId}` (operationId `Inbox_Get`)."""
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/inbox/{inbox_id}",
        params=params,
    )
    return Inbox.model_validate(response.json)


def inbox_post_attachment_by_inbox_id(
    transport: Transport,
    *,
    organisation_id: int,
    inbox_id: int,
    body: list[InboxAttachment],
) -> int | None:
    """`POST /api/orgs/{organisationId}/inbox/{inboxId}` (operationId `Inbox_PostAttachment`)."""
    response = transport.request(
        "POST",
        f"/api/orgs/{organisation_id}/inbox/{inbox_id}",
        json=[item.model_dump(by_alias=True, exclude_none=True) for item in body],
    )
    return response.location_id


def inbox_delete_by_inbox_id(
    transport: Transport,
    *,
    organisation_id: int,
    inbox_id: int,
) -> None:
    """`DELETE /api/orgs/{organisationId}/inbox/{inboxId}` (operationId `Inbox_Delete`)."""
    transport.request("DELETE", f"/api/orgs/{organisation_id}/inbox/{inbox_id}")
    return None


def inbox_delete_attachment(
    transport: Transport,
    *,
    organisation_id: int,
    inbox_id: int,
    inbox_attachment_id: int,
) -> None:
    """`DELETE /api/orgs/{organisationId}/inbox/{inboxId}/attachments/{inboxAttachmentId}`
    (operationId `Inbox_DeleteAttachment`).
    """
    transport.request(
        "DELETE",
        f"/api/orgs/{organisation_id}/inbox/{inbox_id}/attachments/{inbox_attachment_id}",
    )
    return None


def inbox_put(
    transport: Transport,
    *,
    organisation_id: int,
    inbox_id: int,
    action_name: str,
) -> None:
    """`PUT /api/orgs/{organisationId}/inbox/{inboxId}/actions/{actionName}` (operationId
    `Inbox_Put`).
    """
    transport.request("PUT", f"/api/orgs/{organisation_id}/inbox/{inbox_id}/actions/{action_name}")
    return None


def issued_invoice_get(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[IssuedInvoiceSearch]:
    """`GET /api/orgs/{organisationId}/issuedinvoices` (operationId `IssuedInvoice_Get`)."""
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/issuedinvoices",
        params=params,
    )
    return SearchResult[IssuedInvoiceSearch].model_validate(response.json)


def issued_invoice_post(
    transport: Transport,
    *,
    organisation_id: int,
    body: IssuedInvoice,
) -> int | None:
    """`POST /api/orgs/{organisationId}/issuedinvoices` (operationId `IssuedInvoice_Post`)."""
    response = transport.request(
        "POST",
        f"/api/orgs/{organisation_id}/issuedinvoices",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return response.location_id


def issued_invoice_get_by_issued_invoice_id(
    transport: Transport,
    *,
    organisation_id: int,
    issued_invoice_id: int,
    params: Mapping[str, Any] | None = None,
) -> IssuedInvoice:
    """`GET /api/orgs/{organisationId}/issuedinvoices/{issuedInvoiceId}` (operationId
    `IssuedInvoice_Get`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/issuedinvoices/{issued_invoice_id}",
        params=params,
    )
    return IssuedInvoice.model_validate(response.json)


def issued_invoice_put_by_issued_invoice_id(
    transport: Transport,
    *,
    organisation_id: int,
    issued_invoice_id: int,
    body: IssuedInvoice,
) -> None:
    """`PUT /api/orgs/{organisationId}/issuedinvoices/{issuedInvoiceId}` (operationId
    `IssuedInvoice_Put`).
    """
    transport.request(
        "PUT",
        f"/api/orgs/{organisation_id}/issuedinvoices/{issued_invoice_id}",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return None


def issued_invoice_delete_by_issued_invoice_id(
    transport: Transport,
    *,
    organisation_id: int,
    issued_invoice_id: int,
) -> None:
    """`DELETE /api/orgs/{organisationId}/issuedinvoices/{issuedInvoiceId}` (operationId
    `IssuedInvoice_Delete`).
    """
    transport.request("DELETE", f"/api/orgs/{organisation_id}/issuedinvoices/{issued_invoice_id}")
    return None


def issued_invoice_put_by_issued_invoice_id_actions_by_action_name(
    transport: Transport,
    *,
    organisation_id: int,
    issued_invoice_id: int,
    action_name: str,
    params: Mapping[str, Any] | None = None,
) -> None:
    """`PUT /api/orgs/{organisationId}/issuedinvoices/{issuedInvoiceId}/actions/{actionName}`
    (operationId `IssuedInvoice_Put`).
    """
    transport.request(
        "PUT",
        f"/api/orgs/{organisation_id}/issuedinvoices/{issued_invoice_id}/actions/{action_name}",
        params=params,
    )
    return None


def issued_invoice_get_issued_invoices_sync_candidates(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SyncQueryResult:
    """`GET /api/orgs/{organisationId}/issuedinvoices/synccandidates` (operationId
    `IssuedInvoice_GetIssuedInvoicesSyncCandidates`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/issuedinvoices/synccandidates",
        params=params,
    )
    return SyncQueryResult.model_validate(response.json)


def issued_invoice_get_payment_methods(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[IssuedInvoicePaymentMethodSearch]:
    """`GET /api/orgs/{organisationId}/issuedinvoices/paymentmethods` (operationId
    `IssuedInvoice_GetPaymentMethods`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/issuedinvoices/paymentmethods",
        params=params,
    )
    return SearchResult[IssuedInvoicePaymentMethodSearch].model_validate(response.json)


def issued_invoice_get_attachments(
    transport: Transport,
    *,
    organisation_id: int,
    issued_invoice_id: int,
    params: Mapping[str, Any] | None = None,
) -> None:
    """`GET /api/orgs/{organisationId}/issuedinvoices/{issuedInvoiceId}/attachments` (operationId
    `IssuedInvoice_GetAttachments`).
    """
    transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/issuedinvoices/{issued_invoice_id}/attachments",
        params=params,
    )
    return None


def issued_invoice_post_add_attachment(
    transport: Transport,
    *,
    organisation_id: int,
    issued_invoice_id: int,
    body: Attachment,
) -> int | None:
    """`POST /api/orgs/{organisationId}/issuedinvoices/{issuedInvoiceId}/attachments` (operationId
    `IssuedInvoice_PostAddAttachment`).
    """
    response = transport.request(
        "POST",
        f"/api/orgs/{organisation_id}/issuedinvoices/{issued_invoice_id}/attachments",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return response.location_id


def issued_invoice_posting_get(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[IssuedInvoicePostingSearch]:
    """`GET /api/orgs/{organisationId}/issuedinvoicepostings` (operationId
    `IssuedInvoicePosting_Get`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/issuedinvoicepostings",
        params=params,
    )
    return SearchResult[IssuedInvoicePostingSearch].model_validate(response.json)


def issued_invoice_posting_post(
    transport: Transport,
    *,
    organisation_id: int,
    body: IssuedInvoicePosting,
) -> int | None:
    """`POST /api/orgs/{organisationId}/issuedinvoicepostings` (operationId
    `IssuedInvoicePosting_Post`).
    """
    response = transport.request(
        "POST",
        f"/api/orgs/{organisation_id}/issuedinvoicepostings",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return response.location_id


def issued_invoice_posting_get_by_issued_invoice_posting_id(
    transport: Transport,
    *,
    organisation_id: int,
    issued_invoice_posting_id: int,
    params: Mapping[str, Any] | None = None,
) -> IssuedInvoicePosting:
    """`GET /api/orgs/{organisationId}/issuedinvoicepostings/{issuedInvoicePostingId}` (operationId
    `IssuedInvoicePosting_Get`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/issuedinvoicepostings/{issued_invoice_posting_id}",
        params=params,
    )
    return IssuedInvoicePosting.model_validate(response.json)


def issued_invoice_posting_delete_by_issued_invoice_posting_id(
    transport: Transport,
    *,
    organisation_id: int,
    issued_invoice_posting_id: int,
) -> None:
    """`DELETE /api/orgs/{organisationId}/issuedinvoicepostings/{issuedInvoicePostingId}`
    (operationId `IssuedInvoicePosting_Delete`).
    """
    transport.request(
        "DELETE",
        f"/api/orgs/{organisation_id}/issuedinvoicepostings/{issued_invoice_posting_id}",
    )
    return None


def issued_invoice_posting_get_payment_methods(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[IssuedInvoicePostingPaymentMethodSearch]:
    """`GET /api/orgs/{organisationId}/issuedinvoicepostings/paymentmethods` (operationId
    `IssuedInvoicePosting_GetPaymentMethods`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/issuedinvoicepostings/paymentmethods",
        params=params,
    )
    return SearchResult[IssuedInvoicePostingPaymentMethodSearch].model_validate(response.json)


def issued_invoice_posting_put(
    transport: Transport,
    *,
    organisation_id: int,
    issued_invoice_posting_id: int,
    action_name: str,
) -> None:
    """`PUT
    /api/orgs/{organisationId}/issuedinvoicepostings/{issuedInvoicePostingId}/actions/{actionName}`
    (operationId `IssuedInvoicePosting_Put`).
    """
    transport.request(
        "PUT",
        f"/api/orgs/{organisation_id}/issuedinvoicepostings/{issued_invoice_posting_id}/actions"
        f"/{action_name}",
    )
    return None


def item_get(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[ItemSearch]:
    """`GET /api/orgs/{organisationId}/items` (operationId `Item_Get`)."""
    response = transport.request("GET", f"/api/orgs/{organisation_id}/items", params=params)
    return SearchResult[ItemSearch].model_validate(response.json)


def item_post(
    transport: Transport,
    *,
    organisation_id: int,
    body: Item,
) -> int | None:
    """`POST /api/orgs/{organisationId}/items` (operationId `Item_Post`)."""
    response = transport.request(
        "POST",
        f"/api/orgs/{organisation_id}/items",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return response.location_id


def item_get_by_item_id(
    transport: Transport,
    *,
    organisation_id: int,
    item_id: int,
    params: Mapping[str, Any] | None = None,
) -> Item:
    """`GET /api/orgs/{organisationId}/items/{itemId}` (operationId `Item_Get`)."""
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/items/{item_id}",
        params=params,
    )
    return Item.model_validate(response.json)


def item_put_by_item_id(
    transport: Transport,
    *,
    organisation_id: int,
    item_id: int,
    body: Item,
) -> None:
    """`PUT /api/orgs/{organisationId}/items/{itemId}` (operationId `Item_Put`)."""
    transport.request(
        "PUT",
        f"/api/orgs/{organisation_id}/items/{item_id}",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return None


def item_delete_by_item_id(
    transport: Transport,
    *,
    organisation_id: int,
    item_id: int,
) -> None:
    """`DELETE /api/orgs/{organisationId}/items/{itemId}` (operationId `Item_Delete`)."""
    transport.request("DELETE", f"/api/orgs/{organisation_id}/items/{item_id}")
    return None


def item_get_by_code(
    transport: Transport,
    *,
    organisation_id: int,
    code: str,
    params: Mapping[str, Any] | None = None,
) -> Item:
    """`GET /api/orgs/{organisationId}/items/code({code})` (operationId `Item_Get`)."""
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/items/code({code})",
        params=params,
    )
    return Item.model_validate(response.json)


def item_get_items_settings(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> ItemsSettings:
    """`GET /api/orgs/{organisationId}/items/settings` (operationId `Item_GetItemsSettings`)."""
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/items/settings",
        params=params,
    )
    return ItemsSettings.model_validate(response.json)


def item_get_items_data(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> ItemDataListResult:
    """`GET /api/orgs/{organisationId}/items/itemsdata` (operationId `Item_GetItemsData`)."""
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/items/itemsdata",
        params=params,
    )
    return ItemDataListResult.model_validate(response.json)


def item_get_price_lists(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> ItemPriceListItemListResult:
    """`GET /api/orgs/{organisationId}/items/pricelists` (operationId `Item_GetPriceLists`)."""
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/items/pricelists",
        params=params,
    )
    return ItemPriceListItemListResult.model_validate(response.json)


def item_get_items_sync_candidates(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SyncQueryResult:
    """`GET /api/orgs/{organisationId}/items/synccandidates` (operationId
    `Item_GetItemsSyncCandidates`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/items/synccandidates",
        params=params,
    )
    return SyncQueryResult.model_validate(response.json)


def journal_get(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[JournalSearch]:
    """`GET /api/orgs/{organisationId}/journals` (operationId `Journal_Get`)."""
    response = transport.request("GET", f"/api/orgs/{organisation_id}/journals", params=params)
    return SearchResult[JournalSearch].model_validate(response.json)


def journal_post(
    transport: Transport,
    *,
    organisation_id: int,
    body: Journal,
) -> int | None:
    """`POST /api/orgs/{organisationId}/journals` (operationId `Journal_Post`)."""
    response = transport.request(
        "POST",
        f"/api/orgs/{organisation_id}/journals",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return response.location_id


def journal_get_by_journal_id(
    transport: Transport,
    *,
    organisation_id: int,
    journal_id: int,
    params: Mapping[str, Any] | None = None,
) -> Journal:
    """`GET /api/orgs/{organisationId}/journals/{journalId}` (operationId `Journal_Get`)."""
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/journals/{journal_id}",
        params=params,
    )
    return Journal.model_validate(response.json)


def journal_put_by_journal_id(
    transport: Transport,
    *,
    organisation_id: int,
    journal_id: int,
    body: Journal,
) -> None:
    """`PUT /api/orgs/{organisationId}/journals/{journalId}` (operationId `Journal_Put`)."""
    transport.request(
        "PUT",
        f"/api/orgs/{organisation_id}/journals/{journal_id}",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return None


def journal_delete_by_journal_id(
    transport: Transport,
    *,
    organisation_id: int,
    journal_id: int,
) -> None:
    """`DELETE /api/orgs/{organisationId}/journals/{journalId}` (operationId `Journal_Delete`)."""
    transport.request("DELETE", f"/api/orgs/{organisation_id}/journals/{journal_id}")
    return None


def journal_get_by_journal_id_vat_by_vat_id(
    transport: Transport,
    *,
    organisation_id: int,
    journal_id: int,
    vat_id: int,
    params: Mapping[str, Any] | None = None,
) -> VATEntry:
    """`GET /api/orgs/{organisationId}/journals/{journalId}/vat/{vatId}` (operationId
    `Journal_Get`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/journals/{journal_id}/vat/{vat_id}",
        params=params,
    )
    return VATEntry.model_validate(response.json)


def journal_put_by_journal_id_vat_by_vat_id(
    transport: Transport,
    *,
    organisation_id: int,
    journal_id: int,
    vat_id: int,
    body: VATEntry,
) -> None:
    """`PUT /api/orgs/{organisationId}/journals/{journalId}/vat/{vatId}` (operationId
    `Journal_Put`).
    """
    transport.request(
        "PUT",
        f"/api/orgs/{organisation_id}/journals/{journal_id}/vat/{vat_id}",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return None


def journal_delete_by_journal_id_vat_by_vat_id(
    transport: Transport,
    *,
    organisation_id: int,
    journal_id: int,
    vat_id: int,
) -> None:
    """`DELETE /api/orgs/{organisationId}/journals/{journalId}/vat/{vatId}` (operationId
    `Journal_Delete`).
    """
    transport.request("DELETE", f"/api/orgs/{organisation_id}/journals/{journal_id}/vat/{vat_id}")
    return None


def journal_post_by_journal_id_vat(
    transport: Transport,
    *,
    organisation_id: int,
    journal_id: int,
    body: VATEntry,
) -> int | None:
    """`POST /api/orgs/{organisationId}/journals/{journalId}/vat` (operationId `Journal_Post`)."""
    response = transport.request(
        "POST",
        f"/api/orgs/{organisation_id}/journals/{journal_id}/vat",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return response.location_id


def journal_get_journals_sync_candidates(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SyncQueryResult:
    """`GET /api/orgs/{organisationId}/journals/synccandidates` (operationId
    `Journal_GetJournalsSyncCandidates`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/journals/synccandidates",
        params=params,
    )
    return SyncQueryResult.model_validate(response.json)


def journal_get_journals_in_vod_standard(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> None:
    """`GET /api/orgs/{organisationId}/journals/vodstandard` (operationId
    `Journal_GetJournalsInVODStandard`).
    """
    transport.request("GET", f"/api/orgs/{organisation_id}/journals/vodstandard", params=params)
    return None


def journal_get_journal_entries(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[JournalEntries]:
    """`GET /api/orgs/{organisationId}/journals/journal-entries` (operationId
    `Journal_GetJournalEntries`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/journals/journal-entries",
        params=params,
    )
    return SearchResult[JournalEntries].model_validate(response.json)


def journal_type_get(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[JournalType]:
    """`GET /api/orgs/{organisationId}/journaltypes` (operationId `JournalType_Get`)."""
    response = transport.request("GET", f"/api/orgs/{organisation_id}/journaltypes", params=params)
    return SearchResult[JournalType].model_validate(response.json)


def journal_type_get_by_journal_type_id(
    transport: Transport,
    *,
    organisation_id: int,
    journal_type_id: int,
    params: Mapping[str, Any] | None = None,
) -> JournalType:
    """`GET /api/orgs/{organisationId}/journaltypes/{journalTypeId}` (operationId
    `JournalType_Get`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/journaltypes/{journal_type_id}",
        params=params,
    )
    return JournalType.model_validate(response.json)


def journal_type_get_by_code(
    transport: Transport,
    *,
    organisation_id: int,
    code: str,
    params: Mapping[str, Any] | None = None,
) -> JournalType:
    """`GET /api/orgs/{organisationId}/journaltypes/code({code})` (operationId `JournalType_Get`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/journaltypes/code({code})",
        params=params,
    )
    return JournalType.model_validate(response.json)


def journal_type_get_journal_types_sync_candidates(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SyncQueryResult:
    """`GET /api/orgs/{organisationId}/journaltypes/synccandidates` (operationId
    `JournalType_GetJournalTypesSyncCandidates`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/journaltypes/synccandidates",
        params=params,
    )
    return SyncQueryResult.model_validate(response.json)


def order_get(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[OrderSearch]:
    """`GET /api/orgs/{organisationId}/orders` (operationId `Order_Get`)."""
    response = transport.request("GET", f"/api/orgs/{organisation_id}/orders", params=params)
    return SearchResult[OrderSearch].model_validate(response.json)


def order_post(
    transport: Transport,
    *,
    organisation_id: int,
    body: Order,
) -> int | None:
    """`POST /api/orgs/{organisationId}/orders` (operationId `Order_Post`)."""
    response = transport.request(
        "POST",
        f"/api/orgs/{organisation_id}/orders",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return response.location_id


def order_get_by_order_id(
    transport: Transport,
    *,
    organisation_id: int,
    order_id: int,
    params: Mapping[str, Any] | None = None,
) -> Order:
    """`GET /api/orgs/{organisationId}/orders/{orderId}` (operationId `Order_Get`)."""
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/orders/{order_id}",
        params=params,
    )
    return Order.model_validate(response.json)


def order_put_by_order_id(
    transport: Transport,
    *,
    organisation_id: int,
    order_id: int,
    body: Order,
) -> None:
    """`PUT /api/orgs/{organisationId}/orders/{orderId}` (operationId `Order_Put`)."""
    transport.request(
        "PUT",
        f"/api/orgs/{organisation_id}/orders/{order_id}",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return None


def order_delete_by_order_id(
    transport: Transport,
    *,
    organisation_id: int,
    order_id: int,
) -> None:
    """`DELETE /api/orgs/{organisationId}/orders/{orderId}` (operationId `Order_Delete`)."""
    transport.request("DELETE", f"/api/orgs/{organisation_id}/orders/{order_id}")
    return None


def order_get_by_order_id_actions_by_action_name(
    transport: Transport,
    *,
    organisation_id: int,
    order_id: int,
    action_name: str,
    params: Mapping[str, Any] | None = None,
) -> None:
    """`GET /api/orgs/{organisationId}/orders/{orderId}/actions/{actionName}` (operationId
    `Order_Get`).
    """
    transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/orders/{order_id}/actions/{action_name}",
        params=params,
    )
    return None


def order_put_by_order_id_actions_by_action_name(
    transport: Transport,
    *,
    organisation_id: int,
    order_id: int,
    action_name: str,
    params: Mapping[str, Any] | None = None,
) -> None:
    """`PUT /api/orgs/{organisationId}/orders/{orderId}/actions/{actionName}` (operationId
    `Order_Put`).
    """
    transport.request(
        "PUT",
        f"/api/orgs/{organisation_id}/orders/{order_id}/actions/{action_name}",
        params=params,
    )
    return None


def order_get_orders_sync_candidates(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SyncQueryResult:
    """`GET /api/orgs/{organisationId}/orders/synccandidates` (operationId
    `Order_GetOrdersSyncCandidates`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/orders/synccandidates",
        params=params,
    )
    return SyncQueryResult.model_validate(response.json)


def organisation_get(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> Organisation:
    """`GET /api/orgs/{organisationId}` (operationId `Organisation_Get`)."""
    response = transport.request("GET", f"/api/orgs/{organisation_id}", params=params)
    return Organisation.model_validate(response.json)


def organisation_get_all(
    transport: Transport,
    *,
    params: Mapping[str, Any] | None = None,
) -> None:
    """`GET /api/orgs/allOrgs` (operationId `Organisation_GetAll`)."""
    transport.request("GET", "/api/orgs/allOrgs", params=params)
    return None


def outbox_get(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[Outbox]:
    """`GET /api/orgs/{organisationId}/outbox` (operationId `Outbox_Get`)."""
    response = transport.request("GET", f"/api/orgs/{organisation_id}/outbox", params=params)
    return SearchResult[Outbox].model_validate(response.json)


def outbox_get_by_outbox_id(
    transport: Transport,
    *,
    organisation_id: int,
    outbox_id: int,
    params: Mapping[str, Any] | None = None,
) -> Outbox:
    """`GET /api/orgs/{organisationId}/outbox/{outboxId}` (operationId `Outbox_Get`)."""
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/outbox/{outbox_id}",
        params=params,
    )
    return Outbox.model_validate(response.json)


def payment_method_get(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[PaymentMethodPaymentMethodSearch]:
    """`GET /api/orgs/{organisationId}/paymentMethods` (operationId `PaymentMethod_Get`)."""
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/paymentMethods",
        params=params,
    )
    return SearchResult[PaymentMethodPaymentMethodSearch].model_validate(response.json)


def payroll_settings_get(
    transport: Transport,
    *,
    payroll_setting_code: str,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[PayrollSettings]:
    """`GET /api/payrollsettings/{payrollSettingCode}` (operationId `PayrollSettings_Get`)."""
    response = transport.request(
        "GET",
        f"/api/payrollsettings/{payroll_setting_code}",
        params=params,
    )
    return SearchResult[PayrollSettings].model_validate(response.json)


def postal_code_get_postal_codes_for_county(
    transport: Transport,
    *,
    organisation_id: int,
    country_id: int,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[PostalCode]:
    """`GET /api/orgs/{organisationId}/postalcodes/countries/{countryId}` (operationId
    `PostalCode_GetPostalCodesForCounty`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/postalcodes/countries/{country_id}",
        params=params,
    )
    return SearchResult[PostalCode].model_validate(response.json)


def postal_code_get_postal_code_by_id(
    transport: Transport,
    *,
    organisation_id: int,
    postal_code_id: int,
    params: Mapping[str, Any] | None = None,
) -> PostalCode:
    """`GET /api/orgs/{organisationId}/postalcodes/{postalCodeId}` (operationId
    `PostalCode_GetPostalCodeByID`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/postalcodes/{postal_code_id}",
        params=params,
    )
    return PostalCode.model_validate(response.json)


def postal_code_get_postal_codes_sync_candidates(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SyncQueryResult:
    """`GET /api/orgs/{organisationId}/postalcodes/synccandidates` (operationId
    `PostalCode_GetPostalCodesSyncCandidates`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/postalcodes/synccandidates",
        params=params,
    )
    return SyncQueryResult.model_validate(response.json)


def product_group_get(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[ProductGroup]:
    """`GET /api/orgs/{organisationId}/productGroups` (operationId `ProductGroup_Get`)."""
    response = transport.request("GET", f"/api/orgs/{organisation_id}/productGroups", params=params)
    return SearchResult[ProductGroup].model_validate(response.json)


def product_group_post(
    transport: Transport,
    *,
    organisation_id: int,
    body: ProductGroup,
) -> int | None:
    """`POST /api/orgs/{organisationId}/productGroups` (operationId `ProductGroup_Post`)."""
    response = transport.request(
        "POST",
        f"/api/orgs/{organisation_id}/productGroups",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return response.location_id


def product_group_get_by_product_group_id(
    transport: Transport,
    *,
    organisation_id: int,
    product_group_id: int,
    params: Mapping[str, Any] | None = None,
) -> ProductGroup:
    """`GET /api/orgs/{organisationId}/productGroups/{productGroupId}` (operationId
    `ProductGroup_Get`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/productGroups/{product_group_id}",
        params=params,
    )
    return ProductGroup.model_validate(response.json)


def product_group_put_by_product_group_id(
    transport: Transport,
    *,
    organisation_id: int,
    product_group_id: int,
    body: ProductGroup,
) -> None:
    """`PUT /api/orgs/{organisationId}/productGroups/{productGroupId}` (operationId
    `ProductGroup_Put`).
    """
    transport.request(
        "PUT",
        f"/api/orgs/{organisation_id}/productGroups/{product_group_id}",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return None


def product_group_delete_by_product_group_id(
    transport: Transport,
    *,
    organisation_id: int,
    product_group_id: int,
) -> None:
    """`DELETE /api/orgs/{organisationId}/productGroups/{productGroupId}` (operationId
    `ProductGroup_Delete`).
    """
    transport.request("DELETE", f"/api/orgs/{organisation_id}/productGroups/{product_group_id}")
    return None


def product_group_get_product_groups_sync_candidates(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SyncQueryResult:
    """`GET /api/orgs/{organisationId}/productGroups/synccandidates` (operationId
    `ProductGroup_GetProductGroupsSyncCandidates`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/productGroups/synccandidates",
        params=params,
    )
    return SyncQueryResult.model_validate(response.json)


def purpose_code_get(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[PurposeCode]:
    """`GET /api/orgs/{organisationId}/purpose-codes` (operationId `PurposeCode_Get`)."""
    response = transport.request("GET", f"/api/orgs/{organisation_id}/purpose-codes", params=params)
    return SearchResult[PurposeCode].model_validate(response.json)


def purpose_code_get_by_purpose_code_id(
    transport: Transport,
    *,
    organisation_id: int,
    purpose_code_id: int,
    params: Mapping[str, Any] | None = None,
) -> PurposeCode:
    """`GET /api/orgs/{organisationId}/purpose-codes/{purposeCodeId}` (operationId
    `PurposeCode_Get`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/purpose-codes/{purpose_code_id}",
        params=params,
    )
    return PurposeCode.model_validate(response.json)


def purpose_code_get_by_code(
    transport: Transport,
    *,
    organisation_id: int,
    code: str,
    params: Mapping[str, Any] | None = None,
) -> PurposeCode:
    """`GET /api/orgs/{organisationId}/purpose-codes/code({code})` (operationId `PurposeCode_Get`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/purpose-codes/code({code})",
        params=params,
    )
    return PurposeCode.model_validate(response.json)


def purpose_code_get_purpose_codes_sync_candidates(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SyncQueryResult:
    """`GET /api/orgs/{organisationId}/purpose-codes/synccandidates` (operationId
    `PurposeCode_GetPurposeCodesSyncCandidates`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/purpose-codes/synccandidates",
        params=params,
    )
    return SyncQueryResult.model_validate(response.json)


def received_invoice_get_by_received_invoice_id(
    transport: Transport,
    *,
    organisation_id: int,
    received_invoice_id: int,
    params: Mapping[str, Any] | None = None,
) -> ReceivedInvoice:
    """`GET /api/orgs/{organisationId}/receivedinvoices/{receivedInvoiceId}` (operationId
    `ReceivedInvoice_Get`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/receivedinvoices/{received_invoice_id}",
        params=params,
    )
    return ReceivedInvoice.model_validate(response.json)


def received_invoice_put_by_received_invoice_id(
    transport: Transport,
    *,
    organisation_id: int,
    received_invoice_id: int,
    body: ReceivedInvoice,
) -> None:
    """`PUT /api/orgs/{organisationId}/receivedinvoices/{receivedInvoiceId}` (operationId
    `ReceivedInvoice_Put`).
    """
    transport.request(
        "PUT",
        f"/api/orgs/{organisation_id}/receivedinvoices/{received_invoice_id}",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return None


def received_invoice_delete_by_received_invoice_id(
    transport: Transport,
    *,
    organisation_id: int,
    received_invoice_id: int,
) -> None:
    """`DELETE /api/orgs/{organisationId}/receivedinvoices/{receivedInvoiceId}` (operationId
    `ReceivedInvoice_Delete`).
    """
    transport.request(
        "DELETE",
        f"/api/orgs/{organisation_id}/receivedinvoices/{received_invoice_id}",
    )
    return None


def received_invoice_get(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[ReceivedInvoiceSearch]:
    """`GET /api/orgs/{organisationId}/receivedinvoices` (operationId `ReceivedInvoice_Get`)."""
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/receivedinvoices",
        params=params,
    )
    return SearchResult[ReceivedInvoiceSearch].model_validate(response.json)


def received_invoice_post(
    transport: Transport,
    *,
    organisation_id: int,
    body: ReceivedInvoice,
) -> int | None:
    """`POST /api/orgs/{organisationId}/receivedinvoices` (operationId `ReceivedInvoice_Post`)."""
    response = transport.request(
        "POST",
        f"/api/orgs/{organisation_id}/receivedinvoices",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return response.location_id


def received_invoice_get_attachments(
    transport: Transport,
    *,
    organisation_id: int,
    received_invoice_id: int,
    params: Mapping[str, Any] | None = None,
) -> None:
    """`GET /api/orgs/{organisationId}/receivedinvoices/{receivedInvoiceId}/attachments`
    (operationId `ReceivedInvoice_GetAttachments`).
    """
    transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/receivedinvoices/{received_invoice_id}/attachments",
        params=params,
    )
    return None


def received_invoice_post_add_attachment(
    transport: Transport,
    *,
    organisation_id: int,
    received_invoice_id: int,
    body: Attachment,
) -> int | None:
    """`POST /api/orgs/{organisationId}/receivedinvoices/{receivedInvoiceId}/attachments`
    (operationId `ReceivedInvoice_PostAddAttachment`).
    """
    response = transport.request(
        "POST",
        f"/api/orgs/{organisation_id}/receivedinvoices/{received_invoice_id}/attachments",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return response.location_id


def report_template_get(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[ReportTemplate]:
    """`GET /api/orgs/{organisationId}/report-templates` (operationId `ReportTemplate_Get`)."""
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/report-templates",
        params=params,
    )
    return SearchResult[ReportTemplate].model_validate(response.json)


def report_template_get_by_report_template_id(
    transport: Transport,
    *,
    organisation_id: int,
    report_template_id: int,
    params: Mapping[str, Any] | None = None,
) -> ReportTemplate:
    """`GET /api/orgs/{organisationId}/report-templates/{reportTemplateId}` (operationId
    `ReportTemplate_Get`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/report-templates/{report_template_id}",
        params=params,
    )
    return ReportTemplate.model_validate(response.json)


def report_template_get_report_template_sync_candidates(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SyncQueryResult:
    """`GET /api/orgs/{organisationId}/report-templates/synccandidates` (operationId
    `ReportTemplate_GetReportTemplateSyncCandidates`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/report-templates/synccandidates",
        params=params,
    )
    return SyncQueryResult.model_validate(response.json)


def stock_get(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[StockListItem]:
    """`GET /api/orgs/{organisationId}/stocks` (operationId `Stock_Get`)."""
    response = transport.request("GET", f"/api/orgs/{organisation_id}/stocks", params=params)
    return SearchResult[StockListItem].model_validate(response.json)


def stock_get_by_item_id(
    transport: Transport,
    *,
    organisation_id: int,
    item_id: int,
    params: Mapping[str, Any] | None = None,
) -> StockListItem:
    """`GET /api/orgs/{organisationId}/stocks/{itemId}` (operationId `Stock_Get`)."""
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/stocks/{item_id}",
        params=params,
    )
    return StockListItem.model_validate(response.json)


def stock_entry_get(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[StockEntrySearch]:
    """`GET /api/orgs/{organisationId}/stockentry` (operationId `StockEntry_Get`)."""
    response = transport.request("GET", f"/api/orgs/{organisation_id}/stockentry", params=params)
    return SearchResult[StockEntrySearch].model_validate(response.json)


def stock_entry_post(
    transport: Transport,
    *,
    organisation_id: int,
    body: StockEntry,
) -> int | None:
    """`POST /api/orgs/{organisationId}/stockentry` (operationId `StockEntry_Post`)."""
    response = transport.request(
        "POST",
        f"/api/orgs/{organisation_id}/stockentry",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return response.location_id


def stock_entry_get_by_stock_entry_id(
    transport: Transport,
    *,
    organisation_id: int,
    stock_entry_id: int,
    params: Mapping[str, Any] | None = None,
) -> StockEntry:
    """`GET /api/orgs/{organisationId}/stockentry/{stockEntryId}` (operationId `StockEntry_Get`)."""
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/stockentry/{stock_entry_id}",
        params=params,
    )
    return StockEntry.model_validate(response.json)


def stock_entry_put_by_stock_entry_id(
    transport: Transport,
    *,
    organisation_id: int,
    stock_entry_id: int,
    body: StockEntry,
) -> None:
    """`PUT /api/orgs/{organisationId}/stockentry/{stockEntryId}` (operationId `StockEntry_Put`)."""
    transport.request(
        "PUT",
        f"/api/orgs/{organisation_id}/stockentry/{stock_entry_id}",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return None


def stock_entry_delete_by_stock_entry_id(
    transport: Transport,
    *,
    organisation_id: int,
    stock_entry_id: int,
) -> None:
    """`DELETE /api/orgs/{organisationId}/stockentry/{stockEntryId}` (operationId
    `StockEntry_Delete`).
    """
    transport.request("DELETE", f"/api/orgs/{organisation_id}/stockentry/{stock_entry_id}")
    return None


def stock_entry_get_by_stock_entry_id_actions_by_action_name(
    transport: Transport,
    *,
    organisation_id: int,
    stock_entry_id: int,
    action_name: str,
    params: Mapping[str, Any] | None = None,
) -> None:
    """`GET /api/orgs/{organisationId}/stockentry/{stockEntryId}/actions/{actionName}` (operationId
    `StockEntry_Get`).
    """
    transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/stockentry/{stock_entry_id}/actions/{action_name}",
        params=params,
    )
    return None


def stock_entry_put_by_stock_entry_id_actions_by_action_name(
    transport: Transport,
    *,
    organisation_id: int,
    stock_entry_id: int,
    action_name: str,
    params: Mapping[str, Any] | None = None,
) -> None:
    """`PUT /api/orgs/{organisationId}/stockentry/{stockEntryId}/actions/{actionName}` (operationId
    `StockEntry_Put`).
    """
    transport.request(
        "PUT",
        f"/api/orgs/{organisation_id}/stockentry/{stock_entry_id}/actions/{action_name}",
        params=params,
    )
    return None


def user_get(
    transport: Transport,
    *,
    params: Mapping[str, Any] | None = None,
) -> User:
    """`GET /api/currentuser/profile` (operationId `User_Get`)."""
    response = transport.request("GET", "/api/currentuser/profile", params=params)
    return User.model_validate(response.json)


def user_get_user_organisations(
    transport: Transport,
    *,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[UserOrganisation]:
    """`GET /api/currentuser/orgs` (operationId `User_GetUserOrganisations`)."""
    response = transport.request("GET", "/api/currentuser/orgs", params=params)
    return SearchResult[UserOrganisation].model_validate(response.json)


def vat_accounting_type_get(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[VatAccountingType]:
    """`GET /api/orgs/{organisationId}/vataccountingtypes` (operationId `VatAccountingType_Get`)."""
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/vataccountingtypes",
        params=params,
    )
    return SearchResult[VatAccountingType].model_validate(response.json)


def vat_accounting_type_get_vat_accounting_types_sync_candidates(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SyncQueryResult:
    """`GET /api/orgs/{organisationId}/vataccountingtypes/synccandidates` (operationId
    `VatAccountingType_GetVatAccountingTypesSyncCandidates`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/vataccountingtypes/synccandidates",
        params=params,
    )
    return SyncQueryResult.model_validate(response.json)


def vat_rate_get(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[VatRate]:
    """`GET /api/orgs/{organisationId}/vatrates` (operationId `VatRate_Get`)."""
    response = transport.request("GET", f"/api/orgs/{organisation_id}/vatrates", params=params)
    return SearchResult[VatRate].model_validate(response.json)


def vat_rate_get_by_vat_rate_id(
    transport: Transport,
    *,
    organisation_id: int,
    vat_rate_id: int,
    params: Mapping[str, Any] | None = None,
) -> VatRate:
    """`GET /api/orgs/{organisationId}/vatrates/{vatRateId}` (operationId `VatRate_Get`)."""
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/vatrates/{vat_rate_id}",
        params=params,
    )
    return VatRate.model_validate(response.json)


def vat_rate_get_by_code(
    transport: Transport,
    *,
    organisation_id: int,
    code: str,
    params: Mapping[str, Any] | None = None,
) -> VatRate:
    """`GET /api/orgs/{organisationId}/vatrates/code({code})` (operationId `VatRate_Get`)."""
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/vatrates/code({code})",
        params=params,
    )
    return VatRate.model_validate(response.json)


def vat_rate_get_vat_rates_sync_candidates(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SyncQueryResult:
    """`GET /api/orgs/{organisationId}/vatrates/synccandidates` (operationId
    `VatRate_GetVatRatesSyncCandidates`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/vatrates/synccandidates",
        params=params,
    )
    return SyncQueryResult.model_validate(response.json)


def warehouse_get(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SearchResult[Warehouse]:
    """`GET /api/orgs/{organisationId}/warehouses` (operationId `Warehouse_Get`)."""
    response = transport.request("GET", f"/api/orgs/{organisation_id}/warehouses", params=params)
    return SearchResult[Warehouse].model_validate(response.json)


def warehouse_post(
    transport: Transport,
    *,
    organisation_id: int,
    body: Warehouse,
) -> int | None:
    """`POST /api/orgs/{organisationId}/warehouses` (operationId `Warehouse_Post`)."""
    response = transport.request(
        "POST",
        f"/api/orgs/{organisation_id}/warehouses",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return response.location_id


def warehouse_get_by_warehouse_id(
    transport: Transport,
    *,
    organisation_id: int,
    warehouse_id: int,
    params: Mapping[str, Any] | None = None,
) -> Warehouse:
    """`GET /api/orgs/{organisationId}/warehouses/{warehouseId}` (operationId `Warehouse_Get`)."""
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/warehouses/{warehouse_id}",
        params=params,
    )
    return Warehouse.model_validate(response.json)


def warehouse_put_by_warehouse_id(
    transport: Transport,
    *,
    organisation_id: int,
    warehouse_id: int,
    body: Warehouse,
) -> None:
    """`PUT /api/orgs/{organisationId}/warehouses/{warehouseId}` (operationId `Warehouse_Put`)."""
    transport.request(
        "PUT",
        f"/api/orgs/{organisation_id}/warehouses/{warehouse_id}",
        json=body.model_dump(by_alias=True, exclude_none=True),
    )
    return None


def warehouse_delete_by_warehouse_id(
    transport: Transport,
    *,
    organisation_id: int,
    warehouse_id: int,
) -> None:
    """`DELETE /api/orgs/{organisationId}/warehouses/{warehouseId}` (operationId
    `Warehouse_Delete`).
    """
    transport.request("DELETE", f"/api/orgs/{organisation_id}/warehouses/{warehouse_id}")
    return None


def warehouse_get_warehouses_sync_candidates(
    transport: Transport,
    *,
    organisation_id: int,
    params: Mapping[str, Any] | None = None,
) -> SyncQueryResult:
    """`GET /api/orgs/{organisationId}/warehouses/synccandidates` (operationId
    `Warehouse_GetWarehousesSyncCandidates`).
    """
    response = transport.request(
        "GET",
        f"/api/orgs/{organisation_id}/warehouses/synccandidates",
        params=params,
    )
    return SyncQueryResult.model_validate(response.json)
