"""Models generated from the Minimax Swagger document. Do not edit.

Regenerate with `uv run python scripts/generate.py`.

Generic collection-envelope definitions are skipped: `minimax_api.envelope`
already covers every one of them. `mMApiFkField` is renamed `FkField`.
"""

from __future__ import annotations

from pydantic import Field

from minimax_api.envelope import MinimaxModel


class FkField(MinimaxModel):
    """`SAOP.API.Common.mMApiFkField`"""

    id: int | None = Field(default=None, alias="ID")
    name: str | None = Field(default=None, alias="Name")
    resource_url: str | None = Field(default=None, alias="ResourceUrl")

class mMApiValidationMessage(MinimaxModel):
    """`SAOP.API.Common.mMApiValidationMessage`"""

    message: str | None = Field(default=None, alias="Message")
    property_name: str | None = Field(default=None, alias="PropertyName")

class Account(MinimaxModel):
    """`SAOP.API.Models.Account.Account`"""

    account_id: int | None = Field(default=None, alias="AccountId")
    code: str | None = Field(default=None, alias="Code")
    name: str | None = Field(default=None, alias="Name")
    name_in_other_language: str | None = Field(default=None, alias="NameInOtherLanguage")
    name_in_english: str | None = Field(default=None, alias="NameInEnglish")
    description: str | None = Field(default=None, alias="Description")
    allowed_posting: str | None = Field(default=None, alias="AllowedPosting")
    invoice_accounting: str | None = Field(default=None, alias="InvoiceAccounting")
    analytics_entry: str | None = Field(default=None, alias="AnalyticsEntry")
    employee_entry: str | None = Field(default=None, alias="EmployeeEntry")
    customer_entry: str | None = Field(default=None, alias="CustomerEntry")
    non_taxable: str | None = Field(default=None, alias="NonTaxable")
    application: str | None = Field(default=None, alias="Application")
    valid_from_year: int | None = Field(default=None, alias="ValidFromYear")
    valid_to_year: int | None = Field(default=None, alias="ValidToYear")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class AddressModel(MinimaxModel):
    """`SAOP.API.Models.Address.AddressModel`"""

    address_id: int | None = Field(default=None, alias="AddressId")
    customer: FkField | None = Field(default=None, alias="Customer")
    type_: str | None = Field(default=None, alias="Type")
    name: str | None = Field(default=None, alias="Name")
    gln: str | None = Field(default=None, alias="GLN")
    address: str | None = Field(default=None, alias="Address")
    postal_code: str | None = Field(default=None, alias="PostalCode")
    city: str | None = Field(default=None, alias="City")
    country: FkField | None = Field(default=None, alias="Country")
    country_name: str | None = Field(default=None, alias="CountryName")
    default: str | None = Field(default=None, alias="Default")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class Analytic(MinimaxModel):
    """`SAOP.API.Models.Analytic.Analytic`"""

    analytic_id: int | None = Field(default=None, alias="AnalyticId")
    code: str | None = Field(default=None, alias="Code")
    name: str | None = Field(default=None, alias="Name")
    usage_end_date: str | None = Field(default=None, alias="UsageEndDate")
    parent_analytic: FkField | None = Field(default=None, alias="ParentAnalytic")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class AnalyticSearch(MinimaxModel):
    """`SAOP.API.Models.Analytic.AnalyticSearch`"""

    analytic_id: int | None = Field(default=None, alias="AnalyticId")
    code: str | None = Field(default=None, alias="Code")
    name: str | None = Field(default=None, alias="Name")
    usage_end_date: str | None = Field(default=None, alias="UsageEndDate")
    parent_analytic: FkField | None = Field(default=None, alias="ParentAnalytic")

class Attachment(MinimaxModel):
    """`SAOP.API.Models.Attachment`"""

    attachment_id: int | None = Field(default=None, alias="AttachmentId")
    attachment_data: str | None = Field(default=None, alias="AttachmentData")
    attachment_date: str | None = Field(default=None, alias="AttachmentDate")
    attachment_file_name: str | None = Field(default=None, alias="AttachmentFileName")
    attachment_mime_type: str | None = Field(default=None, alias="AttachmentMimeType")

class BankAccount(MinimaxModel):
    """`SAOP.API.Models.BankAccount.BankAccount`"""

    bank_account_id: int | None = Field(default=None, alias="BankAccountId")
    customer: FkField | None = Field(default=None, alias="Customer")
    name: str | None = Field(default=None, alias="Name")
    iban: str | None = Field(default=None, alias="IBAN")
    account_number: str | None = Field(default=None, alias="AccountNumber")
    bic: str | None = Field(default=None, alias="BIC")
    default: str | None = Field(default=None, alias="Default")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class ClassificationOfProductByActivity(MinimaxModel):
    """`SAOP.API.Models.ClassificationOfProductByActivity.ClassificationOfProductByActivity`"""

    classification_of_product_by_activity_id: int | None = Field(
        default=None, alias="ClassificationOfProductByActivityId"
    )
    code: str | None = Field(default=None, alias="Code")
    description: str | None = Field(default=None, alias="Description")
    valid_from: str | None = Field(default=None, alias="ValidFrom")
    valid_to: str | None = Field(default=None, alias="ValidTo")

class Contact(MinimaxModel):
    """`SAOP.API.Models.Contact.Contact`"""

    contact_id: int | None = Field(default=None, alias="ContactId")
    customer: FkField | None = Field(default=None, alias="Customer")
    full_name: str | None = Field(default=None, alias="FullName")
    phone_number: str | None = Field(default=None, alias="PhoneNumber")
    fax: str | None = Field(default=None, alias="Fax")
    mobile_phone: str | None = Field(default=None, alias="MobilePhone")
    email: str | None = Field(default=None, alias="Email")
    notes: str | None = Field(default=None, alias="Notes")
    default: str | None = Field(default=None, alias="Default")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class Country(MinimaxModel):
    """`SAOP.API.Models.Country.Country`"""

    country_id: int | None = Field(default=None, alias="CountryId")
    code: str | None = Field(default=None, alias="Code")
    name: str | None = Field(default=None, alias="Name")
    currency: FkField | None = Field(default=None, alias="Currency")

class Currency(MinimaxModel):
    """`SAOP.API.Models.Currency.Currency`"""

    currency_id: int | None = Field(default=None, alias="CurrencyId")
    code: str | None = Field(default=None, alias="Code")
    name: str | None = Field(default=None, alias="Name")

class Customer(MinimaxModel):
    """`SAOP.API.Models.Customer.Customer`"""

    customer_id: int | None = Field(default=None, alias="CustomerId")
    code: str | None = Field(default=None, alias="Code")
    name: str | None = Field(default=None, alias="Name")
    address: str | None = Field(default=None, alias="Address")
    postal_code: str | None = Field(default=None, alias="PostalCode")
    city: str | None = Field(default=None, alias="City")
    country: FkField | None = Field(default=None, alias="Country")
    country_name: str | None = Field(default=None, alias="CountryName")
    tax_number: str | None = Field(default=None, alias="TaxNumber")
    registration_number: str | None = Field(default=None, alias="RegistrationNumber")
    vat_identification_number: str | None = Field(default=None, alias="VATIdentificationNumber")
    subject_to_vat: str | None = Field(default=None, alias="SubjectToVAT")
    consider_country_for_bookkeeping: str | None = Field(
        default=None, alias="ConsiderCountryForBookkeeping"
    )
    currency: FkField | None = Field(default=None, alias="Currency")
    expiration_days: int | None = Field(default=None, alias="ExpirationDays")
    rebate_percent: float | None = Field(default=None, alias="RebatePercent")
    web_site_url: str | None = Field(default=None, alias="WebSiteURL")
    e_invoice_issuing: str | None = Field(default=None, alias="EInvoiceIssuing")
    internal_customer_number: str | None = Field(default=None, alias="InternalCustomerNumber")
    gln: str | None = Field(default=None, alias="GLN")
    budget_user_number: str | None = Field(default=None, alias="BudgetUserNumber")
    usage: str | None = Field(default=None, alias="Usage")
    association_type: str | None = Field(default=None, alias="AssociationType")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class CustomerSearch(MinimaxModel):
    """`SAOP.API.Models.Customer.CustomerSearch`"""

    customer_id: int | None = Field(default=None, alias="CustomerId")
    code: str | None = Field(default=None, alias="Code")
    name: str | None = Field(default=None, alias="Name")
    address: str | None = Field(default=None, alias="Address")
    postal_code: str | None = Field(default=None, alias="PostalCode")
    city: str | None = Field(default=None, alias="City")
    country: FkField | None = Field(default=None, alias="Country")
    tax_number: str | None = Field(default=None, alias="TaxNumber")
    usage: str | None = Field(default=None, alias="Usage")

class AgregateInvoice(MinimaxModel):
    """`SAOP.API.Models.Dashboard.AgregateInvoice`"""

    type_: str | None = Field(default=None, alias="Type")
    count: int | None = Field(default=None, alias="Count")
    value: float | None = Field(default=None, alias="Value")

class AgregateInvoiceChart(MinimaxModel):
    """`SAOP.API.Models.Dashboard.Chart[SAOP.API.Models.Dashboard.AgregateInvoice]`"""

    visible: bool | None = Field(default=None, alias="Visible")
    data: list[AgregateInvoice] | None = Field(default=None, alias="Data")

class DashboardCustomerChart(MinimaxModel):
    """`SAOP.API.Models.Dashboard.Chart[SAOP.API.Models.Dashboard.DashboardCustomer]`"""

    visible: bool | None = Field(default=None, alias="Visible")
    data: list[DashboardCustomer] | None = Field(default=None, alias="Data")

class DashboardMonthChart(MinimaxModel):
    """`SAOP.API.Models.Dashboard.Chart[SAOP.API.Models.Dashboard.DashboardMonth]`"""

    visible: bool | None = Field(default=None, alias="Visible")
    data: list[DashboardMonth] | None = Field(default=None, alias="Data")

class Dashboard(MinimaxModel):
    """`SAOP.API.Models.Dashboard.Dashboard`"""

    issued_invoices_summary: AgregateInvoiceChart | None = Field(
        default=None, alias="IssuedInvoicesSummary"
    )
    received_invoices_summary: AgregateInvoiceChart | None = Field(
        default=None, alias="ReceivedInvoicesSummary"
    )
    issued_invoices_unpaid: AgregateInvoiceChart | None = Field(
        default=None, alias="IssuedInvoicesUnpaid"
    )
    received_invoices_unpaid: AgregateInvoiceChart | None = Field(
        default=None, alias="ReceivedInvoicesUnpaid"
    )
    top_customers: DashboardCustomerChart | None = Field(default=None, alias="TopCustomers")
    top_debtors: DashboardCustomerChart | None = Field(default=None, alias="TopDebtors")
    top_suppliers: DashboardCustomerChart | None = Field(default=None, alias="TopSuppliers")
    top_creditors: DashboardCustomerChart | None = Field(default=None, alias="TopCreditors")
    revenues_expenses: DashboardMonthChart | None = Field(default=None, alias="RevenuesExpenses")

class DashboardCustomer(MinimaxModel):
    """`SAOP.API.Models.Dashboard.DashboardCustomer`"""

    position: int | None = Field(default=None, alias="Position")
    customer: str | None = Field(default=None, alias="Customer")
    customer_id: int | None = Field(default=None, alias="CustomerId")
    value: float | None = Field(default=None, alias="Value")

class DashboardMonth(MinimaxModel):
    """`SAOP.API.Models.Dashboard.DashboardMonth`"""

    month: int | None = Field(default=None, alias="Month")
    revenue: float | None = Field(default=None, alias="Revenue")
    expense: float | None = Field(default=None, alias="Expense")

class AttachmentLink(MinimaxModel):
    """`SAOP.API.Models.Document.AttachmentLink`"""

    document_attachment_id: int | None = Field(default=None, alias="DocumentAttachmentId")
    description: str | None = Field(default=None, alias="Description")
    file_name: str | None = Field(default=None, alias="FileName")
    mime_type: str | None = Field(default=None, alias="MimeType")
    entry_date: str | None = Field(default=None, alias="EntryDate")

class Document(MinimaxModel):
    """`SAOP.API.Models.Document.Document`"""

    document_id: int | None = Field(default=None, alias="DocumentId")
    document_date: str | None = Field(default=None, alias="DocumentDate")
    customer: FkField | None = Field(default=None, alias="Customer")
    employee: FkField | None = Field(default=None, alias="Employee")
    description: str | None = Field(default=None, alias="Description")
    attachments: list[AttachmentLink] | None = Field(default=None, alias="Attachments")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class DocumentAttachment(MinimaxModel):
    """`SAOP.API.Models.Document.DocumentAttachment`"""

    document_attachment_id: int | None = Field(default=None, alias="DocumentAttachmentId")
    document: FkField | None = Field(default=None, alias="Document")
    description: str | None = Field(default=None, alias="Description")
    attachment_data: str | None = Field(default=None, alias="AttachmentData")
    file_name: str | None = Field(default=None, alias="FileName")
    mime_type: str | None = Field(default=None, alias="MimeType")
    entry_date: str | None = Field(default=None, alias="EntryDate")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class DocumentSearch(MinimaxModel):
    """`SAOP.API.Models.Document.DocumentSearch`"""

    document_id: int | None = Field(default=None, alias="DocumentId")
    document_date: str | None = Field(default=None, alias="DocumentDate")
    customer: FkField | None = Field(default=None, alias="Customer")
    employee: FkField | None = Field(default=None, alias="Employee")
    description: str | None = Field(default=None, alias="Description")

class DocumentNumbering(MinimaxModel):
    """`SAOP.API.Models.DocumentNumbering.DocumentNumbering`"""

    document_numbering_id: int | None = Field(default=None, alias="DocumentNumberingId")
    document: str | None = Field(default=None, alias="Document")
    code: str | None = Field(default=None, alias="Code")
    name: str | None = Field(default=None, alias="Name")
    default: str | None = Field(default=None, alias="Default")
    reverse: str | None = Field(default=None, alias="Reverse")
    reference_number: str | None = Field(default=None, alias="ReferenceNumber")
    packaging_deposit_return_included_in_price: str | None = Field(
        default=None, alias="PackagingDepositReturnIncludedInPrice"
    )
    usage: str | None = Field(default=None, alias="Usage")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class Employee(MinimaxModel):
    """`SAOP.API.Models.Employee.Employee`"""

    employee_id: int | None = Field(default=None, alias="EmployeeId")
    code: str | None = Field(default=None, alias="Code")
    tax_number: str | None = Field(default=None, alias="TaxNumber")
    first_name: str | None = Field(default=None, alias="FirstName")
    last_name: str | None = Field(default=None, alias="LastName")
    address: str | None = Field(default=None, alias="Address")
    postal_code: str | None = Field(default=None, alias="PostalCode")
    city: str | None = Field(default=None, alias="City")
    country: FkField | None = Field(default=None, alias="Country")
    country_of_residence: FkField | None = Field(default=None, alias="CountryOfResidence")
    date_of_birth: str | None = Field(default=None, alias="DateOfBirth")
    gender: str | None = Field(default=None, alias="Gender")
    employment_start_date: str | None = Field(default=None, alias="EmploymentStartDate")
    employment_end_date: str | None = Field(default=None, alias="EmploymentEndDate")
    notes: str | None = Field(default=None, alias="Notes")
    employment_type: str | None = Field(default=None, alias="EmploymentType")
    personal_idenfication_number: str | None = Field(
        default=None, alias="PersonalIdenficationNumber"
    )
    insurance_basis: str | None = Field(default=None, alias="InsuranceBasis")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class EmployeeSearch(MinimaxModel):
    """`SAOP.API.Models.Employee.EmployeeSearch`"""

    employee_id: int | None = Field(default=None, alias="EmployeeId")
    first_name: str | None = Field(default=None, alias="FirstName")
    last_name: str | None = Field(default=None, alias="LastName")
    date_of_birth: str | None = Field(default=None, alias="DateOfBirth")
    tax_number: str | None = Field(default=None, alias="TaxNumber")
    employment_type: str | None = Field(default=None, alias="EmploymentType")
    employment_start_date: str | None = Field(default=None, alias="EmploymentStartDate")
    employment_end_date: str | None = Field(default=None, alias="EmploymentEndDate")
    country: FkField | None = Field(default=None, alias="Country")
    country_of_residence: FkField | None = Field(default=None, alias="CountryOfResidence")

class ExchangeRate(MinimaxModel):
    """`SAOP.API.Models.ExchangeRate.ExchangeRate`"""

    date: str | None = Field(default=None, alias="Date")
    currency: FkField | None = Field(default=None, alias="Currency")
    mid_rate: float | None = Field(default=None, alias="MidRate")

class Inbox(MinimaxModel):
    """`SAOP.API.Models.Inbox.Inbox`"""

    inbox_id: int | None = Field(default=None, alias="InboxId")
    customer: FkField | None = Field(default=None, alias="Customer")
    employee: FkField | None = Field(default=None, alias="Employee")
    inbox_date: str | None = Field(default=None, alias="InboxDate")
    date_approved: str | None = Field(default=None, alias="DateApproved")
    inbox_type: str | None = Field(default=None, alias="InboxType")
    description: str | None = Field(default=None, alias="Description")
    status_of_received_invoice: str | None = Field(default=None, alias="StatusOfReceivedInvoice")
    bookkeeping_allowed: str | None = Field(default=None, alias="BookkeepingAllowed")
    e_provider: str | None = Field(default=None, alias="EProvider")
    email_subject: str | None = Field(default=None, alias="EmailSubject")
    email_body: str | None = Field(default=None, alias="EmailBody")
    email: str | None = Field(default=None, alias="Email")
    attachments: list[InboxAttachment] | None = Field(default=None, alias="Attachments")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class InboxAttachment(MinimaxModel):
    """`SAOP.API.Models.Inbox.InboxAttachment`"""

    inbox_attachment_id: int | None = Field(default=None, alias="InboxAttachmentId")
    inbox: FkField | None = Field(default=None, alias="Inbox")
    attachment_data: str | None = Field(default=None, alias="AttachmentData")
    attachment_date: str | None = Field(default=None, alias="AttachmentDate")
    attachment_file_name: str | None = Field(default=None, alias="AttachmentFileName")
    attachment_mime_type: str | None = Field(default=None, alias="AttachmentMimeType")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class IssuedInvoice(MinimaxModel):
    """`SAOP.API.Models.IssuedInvoice.IssuedInvoice`"""

    issued_invoice_id: int | None = Field(default=None, alias="IssuedInvoiceId")
    year: int | None = Field(default=None, alias="Year")
    invoice_number: int | None = Field(default=None, alias="InvoiceNumber")
    document_numbering: FkField | None = Field(default=None, alias="DocumentNumbering")
    customer: FkField | None = Field(default=None, alias="Customer")
    date_issued: str | None = Field(default=None, alias="DateIssued")
    date_transaction: str | None = Field(default=None, alias="DateTransaction")
    date_transaction_from: str | None = Field(default=None, alias="DateTransactionFrom")
    date_due: str | None = Field(default=None, alias="DateDue")
    date_credit_note: str | None = Field(default=None, alias="DateCreditNote")
    business_process: str | None = Field(default=None, alias="BusinessProcess")
    addressee_name: str | None = Field(default=None, alias="AddresseeName")
    addressee_address: str | None = Field(default=None, alias="AddresseeAddress")
    addressee_postal_code: str | None = Field(default=None, alias="AddresseePostalCode")
    addressee_city: str | None = Field(default=None, alias="AddresseeCity")
    addressee_country_name: str | None = Field(default=None, alias="AddresseeCountryName")
    addressee_country: FkField | None = Field(default=None, alias="AddresseeCountry")
    addressee_gln: str | None = Field(default=None, alias="AddresseeGLN")
    recipient_name: str | None = Field(default=None, alias="RecipientName")
    recipient_address: str | None = Field(default=None, alias="RecipientAddress")
    recipient_postal_code: str | None = Field(default=None, alias="RecipientPostalCode")
    recipient_city: str | None = Field(default=None, alias="RecipientCity")
    recipient_country_name: str | None = Field(default=None, alias="RecipientCountryName")
    recipient_country: FkField | None = Field(default=None, alias="RecipientCountry")
    recipient_gln: str | None = Field(default=None, alias="RecipientGLN")
    rabate: float | None = Field(default=None, alias="Rabate")
    exchange_rate: float | None = Field(default=None, alias="ExchangeRate")
    document_reference: str | None = Field(default=None, alias="DocumentReference")
    payment_reference: str | None = Field(default=None, alias="PaymentReference")
    currency: FkField | None = Field(default=None, alias="Currency")
    analytic: FkField | None = Field(default=None, alias="Analytic")
    document: FkField | None = Field(default=None, alias="Document")
    issued_invoice_report_template: FkField | None = Field(
        default=None, alias="IssuedInvoiceReportTemplate"
    )
    delivery_note_report_template: FkField | None = Field(
        default=None, alias="DeliveryNoteReportTemplate"
    )
    status: str | None = Field(default=None, alias="Status")
    description_above: str | None = Field(default=None, alias="DescriptionAbove")
    description_below: str | None = Field(default=None, alias="DescriptionBelow")
    delivery_note_description_above: str | None = Field(
        default=None, alias="DeliveryNoteDescriptionAbove"
    )
    delivery_note_description_below: str | None = Field(
        default=None, alias="DeliveryNoteDescriptionBelow"
    )
    notes: str | None = Field(default=None, alias="Notes")
    employee: FkField | None = Field(default=None, alias="Employee")
    prices_on_invoice: str | None = Field(default=None, alias="PricesOnInvoice")
    recurring_invoice: str | None = Field(default=None, alias="RecurringInvoice")
    invoice_for_period: str | None = Field(default=None, alias="InvoiceForPeriod")
    invoice_attachment: FkField | None = Field(default=None, alias="InvoiceAttachment")
    e_invoice_attachment: FkField | None = Field(default=None, alias="EInvoiceAttachment")
    invoice_type: str | None = Field(default=None, alias="InvoiceType")
    original_document_type: str | None = Field(default=None, alias="OriginalDocumentType")
    original_document_date: str | None = Field(default=None, alias="OriginalDocumentDate")
    forward_to_crf: str | None = Field(default=None, alias="ForwardToCRF")
    forward_to_sef: str | None = Field(default=None, alias="ForwardToSEF")
    reverse_reason: str | None = Field(default=None, alias="ReverseReason")
    optional_custumer_data_type: str | None = Field(default=None, alias="OptionalCustumerDataType")
    optional_custumer_data: str | None = Field(default=None, alias="OptionalCustumerData")
    customer_id_type: str | None = Field(default=None, alias="CustomerIDType")
    customer_id: str | None = Field(default=None, alias="CustomerID")
    purpose_code: FkField | None = Field(default=None, alias="PurposeCode")
    payment_status: str | None = Field(default=None, alias="PaymentStatus")
    invoice_value: float | None = Field(default=None, alias="InvoiceValue")
    paid_value: float | None = Field(default=None, alias="PaidValue")
    association_with_stock: str | None = Field(default=None, alias="AssociationWithStock")
    debit_note: str | None = Field(default=None, alias="DebitNote")
    debit_note_basis: str | None = Field(default=None, alias="DebitNoteBasis")
    debit_note_basis_date: str | None = Field(default=None, alias="DebitNoteBasisDate")
    issued_invoice_rows: list[IssuedInvoiceRow] | None = Field(
        default=None, alias="IssuedInvoiceRows"
    )
    issued_invoice_payment_methods: list[IssuedInvoicePaymentMethod] | None = Field(
        default=None, alias="IssuedInvoicePaymentMethods"
    )
    issued_invoice_additional_source_document: (
        list[IssuedInvoiceAdditionalSourceDocument] | None
    ) = Field(default=None, alias="IssuedInvoiceAdditionalSourceDocument")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class IssuedInvoiceAdditionalSourceDocument(MinimaxModel):
    """`SAOP.API.Models.IssuedInvoice.IssuedInvoiceAdditionalSourceDocument`"""

    issued_invoice_additional_source_document_id: int | None = Field(
        default=None, alias="IssuedInvoiceAdditionalSourceDocumentId"
    )
    issued_invoice: FkField | None = Field(default=None, alias="IssuedInvoice")
    source_document_type: str | None = Field(default=None, alias="SourceDocumentType")
    source_document_date: str | None = Field(default=None, alias="SourceDocumentDate")
    source_document_number: str | None = Field(default=None, alias="SourceDocumentNumber")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class IssuedInvoicePaymentMethod(MinimaxModel):
    """`SAOP.API.Models.IssuedInvoice.IssuedInvoicePaymentMethod`"""

    issued_invoice_payment_method_id: int | None = Field(
        default=None, alias="IssuedInvoicePaymentMethodId"
    )
    issued_invoice: FkField | None = Field(default=None, alias="IssuedInvoice")
    payment_method: FkField | None = Field(default=None, alias="PaymentMethod")
    issued_invoice_cancellation: FkField | None = Field(
        default=None, alias="IssuedInvoiceCancellation"
    )
    cash_register: FkField | None = Field(default=None, alias="CashRegister")
    revenue: FkField | None = Field(default=None, alias="Revenue")
    revenue_date: str | None = Field(default=None, alias="RevenueDate")
    amount: float | None = Field(default=None, alias="Amount")
    amount_in_domestic_currency: float | None = Field(
        default=None, alias="AmountInDomesticCurrency"
    )
    already_paid: str | None = Field(default=None, alias="AlreadyPaid")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class IssuedInvoiceRow(MinimaxModel):
    """`SAOP.API.Models.IssuedInvoice.IssuedInvoiceRow`"""

    issued_invoice_row_id: int | None = Field(default=None, alias="IssuedInvoiceRowId")
    issued_invoice: FkField | None = Field(default=None, alias="IssuedInvoice")
    item: FkField | None = Field(default=None, alias="Item")
    item_name: str | None = Field(default=None, alias="ItemName")
    row_number: int | None = Field(default=None, alias="RowNumber")
    item_code: str | None = Field(default=None, alias="ItemCode")
    serial_number: str | None = Field(default=None, alias="SerialNumber")
    batch_number: str | None = Field(default=None, alias="BatchNumber")
    description: str | None = Field(default=None, alias="Description")
    quantity: float | None = Field(default=None, alias="Quantity")
    unit_of_measurement: str | None = Field(default=None, alias="UnitOfMeasurement")
    mass: float | None = Field(default=None, alias="Mass")
    price: float | None = Field(default=None, alias="Price")
    price_with_vat: float | None = Field(default=None, alias="PriceWithVAT")
    vat_percent: float | None = Field(default=None, alias="VATPercent")
    discount: float | None = Field(default=None, alias="Discount")
    discount_percent: float | None = Field(default=None, alias="DiscountPercent")
    value: float | None = Field(default=None, alias="Value")
    vat_rate: FkField | None = Field(default=None, alias="VatRate")
    vat_rate_percentage: FkField | None = Field(default=None, alias="VatRatePercentage")
    warehouse: FkField | None = Field(default=None, alias="Warehouse")
    additional_warehouse: FkField | None = Field(default=None, alias="AdditionalWarehouse")
    tax_free_value: float | None = Field(default=None, alias="TaxFreeValue")
    tax_exemption_value: float | None = Field(default=None, alias="TaxExemptionValue")
    other_taxes_and_duties: str | None = Field(default=None, alias="OtherTaxesAndDuties")
    vat_accounting_type: str | None = Field(default=None, alias="VatAccountingType")
    tax_exemption_reason_code: str | None = Field(default=None, alias="TaxExemptionReasonCode")
    analytic: FkField | None = Field(default=None, alias="Analytic")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class IssuedInvoiceSearch(MinimaxModel):
    """`SAOP.API.Models.IssuedInvoice.IssuedInvoiceSearch`"""

    issued_invoice_id: int | None = Field(default=None, alias="IssuedInvoiceId")
    invoice_type: str | None = Field(default=None, alias="InvoiceType")
    year: int | None = Field(default=None, alias="Year")
    invoice_number: int | None = Field(default=None, alias="InvoiceNumber")
    numbering: str | None = Field(default=None, alias="Numbering")
    document_numbering: FkField | None = Field(default=None, alias="DocumentNumbering")
    customer: FkField | None = Field(default=None, alias="Customer")
    date_issued: str | None = Field(default=None, alias="DateIssued")
    date_transaction: str | None = Field(default=None, alias="DateTransaction")
    date_due: str | None = Field(default=None, alias="DateDue")
    currency: FkField | None = Field(default=None, alias="Currency")
    analytics: FkField | None = Field(default=None, alias="Analytics")
    status: str | None = Field(default=None, alias="Status")
    payment_status: str | None = Field(default=None, alias="PaymentStatus")
    invoice_value: float | None = Field(default=None, alias="InvoiceValue")
    paid_value: float | None = Field(default=None, alias="PaidValue")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class IssuedInvoicePaymentMethodSearch(MinimaxModel):
    """`SAOP.API.Models.IssuedInvoice.PaymentMethodSearch`"""

    payment_method_id: int | None = Field(default=None, alias="PaymentMethodId")
    name: str | None = Field(default=None, alias="Name")
    code: str | None = Field(default=None, alias="Code")
    type_: str | None = Field(default=None, alias="Type")
    usage: str | None = Field(default=None, alias="Usage")

class IssuedInvoicePosting(MinimaxModel):
    """`SAOP.API.Models.IssuedInvoicePosting.IssuedInvoicePosting`"""

    issued_invoice_posting_id: int | None = Field(default=None, alias="IssuedInvoicePostingId")
    document_type: str | None = Field(default=None, alias="DocumentType")
    status: str | None = Field(default=None, alias="Status")
    daily_income_sequential_number: int | None = Field(
        default=None, alias="DailyIncomeSequentialNumber"
    )
    daily_income_invoices_sequential_number_from: int | None = Field(
        default=None, alias="DailyIncomeInvoicesSequentialNumberFrom"
    )
    daily_income_invoices_sequential_number_to: int | None = Field(
        default=None, alias="DailyIncomeInvoicesSequentialNumberTo"
    )
    daily_income_invoices_corrections: int | None = Field(
        default=None, alias="DailyIncomeInvoicesCorrections"
    )
    customer: FkField | None = Field(default=None, alias="Customer")
    date_transaction: str | None = Field(default=None, alias="DateTransaction")
    date_due: str | None = Field(default=None, alias="DateDue")
    payment_reference: str | None = Field(default=None, alias="PaymentReference")
    analytic: FkField | None = Field(default=None, alias="Analytic")
    date: str | None = Field(default=None, alias="Date")
    description: str | None = Field(default=None, alias="Description")
    currency: FkField | None = Field(default=None, alias="Currency")
    exchange_rate: float | None = Field(default=None, alias="ExchangeRate")
    forward_to_sef: str | None = Field(default=None, alias="ForwardToSEF")
    sales_value: float | None = Field(default=None, alias="SalesValue")
    sales_value_vat: float | None = Field(default=None, alias="SalesValueVAT")
    purchase_value: float | None = Field(default=None, alias="PurchaseValue")
    issued_invoice_posting_payment_methods: list[IssuedInvoicePostingPaymentMethod] | None = Field(
        default=None, alias="IssuedInvoicePostingPaymentMethods"
    )
    issued_invoice_posting_taxes: list[IssuedInvoicePostingTax] | None = Field(
        default=None, alias="IssuedInvoicePostingTaxes"
    )
    issued_invoice_posting_revenues: list[IssuedInvoicePostingRevenue] | None = Field(
        default=None, alias="IssuedInvoicePostingRevenues"
    )
    issued_invoice_posting_retail_data_for_bookkeeping: (
        IssuedInvoicePostingRetailDataForBookkeeping | None
    ) = Field(default=None, alias="IssuedInvoicePostingRetailDataForBookkeeping")
    issued_invoice_posting_retail_data_for_value_based_stock_management: (
        IssuedInvoicePostingRetailDataForValueBasedStockManagement | None
    ) = Field(default=None, alias="IssuedInvoicePostingRetailDataForValueBasedStockManagement")
    issued_invoice_posting_retail_data_for_stock_management: (
        IssuedInvoicePostingRetailDataForStockManagement | None
    ) = Field(default=None, alias="IssuedInvoicePostingRetailDataForStockManagement")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class IssuedInvoicePostingPaymentMethod(MinimaxModel):
    """`SAOP.API.Models.IssuedInvoicePosting.IssuedInvoicePostingPaymentMethod`"""

    issued_invoice_posting_payment_method_id: int | None = Field(
        default=None, alias="IssuedInvoicePostingPaymentMethodId"
    )
    issued_invoice_posting: FkField | None = Field(default=None, alias="IssuedInvoicePosting")
    payment_method: FkField | None = Field(default=None, alias="PaymentMethod")
    amount: float | None = Field(default=None, alias="Amount")
    amount_in_domestic_currency: float | None = Field(
        default=None, alias="AmountInDomesticCurrency"
    )
    customer: FkField | None = Field(default=None, alias="Customer")
    advance_payment_issued_invoice_posting_id: int | None = Field(
        default=None, alias="AdvancePaymentIssuedInvoicePostingId"
    )
    cash_register: FkField | None = Field(default=None, alias="CashRegister")
    revenue: FkField | None = Field(default=None, alias="Revenue")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class IssuedInvoicePostingRetailDataForBookkeeping(MinimaxModel):
    """`SAOP.API.Models.IssuedInvoicePosting.IssuedInvoicePostingRetailDataForBookkeeping`"""

    rows: list[IssuedInvoicePostingRetailDataForBookkeepingRow] | None = Field(
        default=None, alias="Rows"
    )

class IssuedInvoicePostingRetailDataForBookkeepingRow(MinimaxModel):
    """`SAOP.API.Models.IssuedInvoicePosting.IssuedInvoicePostingRetailDataForBookkeepingRow`"""

    issued_invoice_posting_retail_id: int | None = Field(
        default=None, alias="IssuedInvoicePostingRetailId"
    )
    issued_invoice_posting: FkField | None = Field(default=None, alias="IssuedInvoicePosting")
    vat_rate: FkField | None = Field(default=None, alias="VatRate")
    purchase_value: float | None = Field(default=None, alias="PurchaseValue")
    sales_value: float | None = Field(default=None, alias="SalesValue")
    sales_value_with_vat: float | None = Field(default=None, alias="SalesValueWithVAT")
    vat: float | None = Field(default=None, alias="VAT")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class IssuedInvoicePostingRetailDataForStockManagement(MinimaxModel):
    """`SAOP.API.Models.IssuedInvoicePosting.IssuedInvoicePostingRetailDataForStockManagement`"""

    warehouse: FkField | None = Field(default=None, alias="Warehouse")
    additional_warehouse: FkField | None = Field(default=None, alias="AdditionalWarehouse")
    rows: list[IssuedInvoicePostingRetailDataForStockManagementRow] | None = Field(
        default=None, alias="Rows"
    )

class IssuedInvoicePostingRetailDataForStockManagementRow(MinimaxModel):
    """`SAOP.API.Models.IssuedInvoicePosting.IssuedInvoicePostingRetailDataForStockManagementRow`"""

    issued_invoice_posting_retail_id: int | None = Field(
        default=None, alias="IssuedInvoicePostingRetailId"
    )
    issued_invoice_posting: FkField | None = Field(default=None, alias="IssuedInvoicePosting")
    item: FkField | None = Field(default=None, alias="Item")
    quantity: float | None = Field(default=None, alias="Quantity")
    price: float | None = Field(default=None, alias="Price")
    purchase_value: float | None = Field(default=None, alias="PurchaseValue")
    selling_price: float | None = Field(default=None, alias="SellingPrice")
    selling_price_includes_vat: str | None = Field(default=None, alias="SellingPriceIncludesVAT")
    batch_number: str | None = Field(default=None, alias="BatchNumber")
    serial_number: str | None = Field(default=None, alias="SerialNumber")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class IssuedInvoicePostingRetailDataForValueBasedStockManagement(MinimaxModel):
    """`SAOP.API.Models.IssuedInvoicePosting.IssuedInvoicePostingRetailDataForValueBasedStockManagement`"""

    warehouse: FkField | None = Field(default=None, alias="Warehouse")
    additional_warehouse: FkField | None = Field(default=None, alias="AdditionalWarehouse")
    rows: list[IssuedInvoicePostingRetailDataForValueBasedStockManagementRow] | None = Field(
        default=None, alias="Rows"
    )

class IssuedInvoicePostingRetailDataForValueBasedStockManagementRow(MinimaxModel):
    """`SAOP.API.Models.IssuedInvoicePosting.IssuedInvoicePostingRetailDataForValueBasedStockManagementRow`"""

    issued_invoice_posting_retail_id: int | None = Field(
        default=None, alias="IssuedInvoicePostingRetailId"
    )
    issued_invoice_posting: FkField | None = Field(default=None, alias="IssuedInvoicePosting")
    vat_rate: FkField | None = Field(default=None, alias="VatRate")
    sales_value: float | None = Field(default=None, alias="SalesValue")
    sales_value_with_vat: float | None = Field(default=None, alias="SalesValueWithVAT")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class IssuedInvoicePostingRevenue(MinimaxModel):
    """`SAOP.API.Models.IssuedInvoicePosting.IssuedInvoicePostingRevenue`"""

    issued_invoice_posting_revenue_id: int | None = Field(
        default=None, alias="IssuedInvoicePostingRevenueId"
    )
    issued_invoice_posting: FkField | None = Field(default=None, alias="IssuedInvoicePosting")
    account: FkField | None = Field(default=None, alias="Account")
    amount: float | None = Field(default=None, alias="Amount")
    amount_in_domestic_currency: float | None = Field(
        default=None, alias="AmountInDomesticCurrency"
    )
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class IssuedInvoicePostingSearch(MinimaxModel):
    """`SAOP.API.Models.IssuedInvoicePosting.IssuedInvoicePostingSearch`"""

    issued_invoice_posting_id: int | None = Field(default=None, alias="IssuedInvoicePostingId")
    document_type: str | None = Field(default=None, alias="DocumentType")
    status: str | None = Field(default=None, alias="Status")
    date: str | None = Field(default=None, alias="Date")
    description: str | None = Field(default=None, alias="Description")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class IssuedInvoicePostingTax(MinimaxModel):
    """`SAOP.API.Models.IssuedInvoicePosting.IssuedInvoicePostingTax`"""

    issued_invoice_posting_tax_id: int | None = Field(
        default=None, alias="IssuedInvoicePostingTaxId"
    )
    issued_invoice_posting: FkField | None = Field(default=None, alias="IssuedInvoicePosting")
    tax_type: str | None = Field(default=None, alias="TaxType")
    tax_subject_type: str | None = Field(default=None, alias="TaxSubjectType")
    vat_rate: FkField | None = Field(default=None, alias="VatRate")
    vat_rate_percentage: FkField | None = Field(default=None, alias="VatRatePercentage")
    tax_percentage: float | None = Field(default=None, alias="TaxPercentage")
    tax_base: float | None = Field(default=None, alias="TaxBase")
    tax_amount: float | None = Field(default=None, alias="TaxAmount")
    tax_base_in_domestic_currency: float | None = Field(
        default=None, alias="TaxBaseInDomesticCurrency"
    )
    tax_amount_in_domestic_currency: float | None = Field(
        default=None, alias="TaxAmountInDomesticCurrency"
    )
    vat_accounting_type: str | None = Field(default=None, alias="VatAccountingType")
    tax_exemption_reason_code: str | None = Field(default=None, alias="TaxExemptionReasonCode")
    advance_payment_issued_invoice_posting_tax_id: int | None = Field(
        default=None, alias="AdvancePaymentIssuedInvoicePostingTaxId"
    )
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class IssuedInvoicePostingPaymentMethodSearch(MinimaxModel):
    """`SAOP.API.Models.IssuedInvoicePosting.PaymentMethodSearch`"""

    payment_method_id: int | None = Field(default=None, alias="PaymentMethodId")
    name: str | None = Field(default=None, alias="Name")
    code: str | None = Field(default=None, alias="Code")
    type_: str | None = Field(default=None, alias="Type")
    usage: str | None = Field(default=None, alias="Usage")

class Item(MinimaxModel):
    """`SAOP.API.Models.Item.Item`"""

    item_id: int | None = Field(default=None, alias="ItemId")
    name: str | None = Field(default=None, alias="Name")
    code: str | None = Field(default=None, alias="Code")
    ean_code: str | None = Field(default=None, alias="EANCode")
    description: str | None = Field(default=None, alias="Description")
    item_type: str | None = Field(default=None, alias="ItemType")
    stocks_managed_only_by_quantity: str | None = Field(
        default=None, alias="StocksManagedOnlyByQuantity"
    )
    calculation_of_consumption_tax: str | None = Field(
        default=None, alias="CalculationOfConsumptionTax"
    )
    unit_of_measurement: str | None = Field(default=None, alias="UnitOfMeasurement")
    mass_per_unit: float | None = Field(default=None, alias="MassPerUnit")
    product_group: FkField | None = Field(default=None, alias="ProductGroup")
    classification_of_product_by_activity: FkField | None = Field(
        default=None, alias="ClassificationOfProductByActivity"
    )
    vat_rate: FkField | None = Field(default=None, alias="VatRate")
    price: float | None = Field(default=None, alias="Price")
    rebate_percent: float | None = Field(default=None, alias="RebatePercent")
    usage: str | None = Field(default=None, alias="Usage")
    currency: FkField | None = Field(default=None, alias="Currency")
    serial_numbers: str | None = Field(default=None, alias="SerialNumbers")
    batch_numbers: str | None = Field(default=None, alias="BatchNumbers")
    revenue_account_domestic: FkField | None = Field(default=None, alias="RevenueAccountDomestic")
    revenue_account_eu: FkField | None = Field(default=None, alias="RevenueAccountEU")
    revenue_account_outside_eu: FkField | None = Field(
        default=None, alias="RevenueAccountOutsideEU"
    )
    stocks_account: FkField | None = Field(default=None, alias="StocksAccount")
    relief_by_composite_from_warehouse: str | None = Field(
        default=None, alias="ReliefByCompositeFromWarehouse"
    )
    relief_by_composite_from_issued_invoice: str | None = Field(
        default=None, alias="ReliefByCompositeFromIssuedInvoice"
    )
    composite: list[ItemComposite] | None = Field(default=None, alias="Composite")
    packaging_deposit_return_quantity: int | None = Field(
        default=None, alias="PackagingDepositReturnQuantity"
    )
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class ItemComposite(MinimaxModel):
    """`SAOP.API.Models.Item.ItemComposite`"""

    item: FkField | None = Field(default=None, alias="Item")
    quantity: float | None = Field(default=None, alias="Quantity")

class ItemData(MinimaxModel):
    """`SAOP.API.Models.Item.ItemData`"""

    title: str | None = Field(default=None, alias="Title")
    code: str | None = Field(default=None, alias="Code")
    price: float | None = Field(default=None, alias="Price")
    unit_of_measurement: str | None = Field(default=None, alias="UnitOfMeasurement")
    item: FkField | None = Field(default=None, alias="Item")
    warehouse: FkField | None = Field(default=None, alias="Warehouse")
    customer: FkField | None = Field(default=None, alias="Customer")

class ItemPriceListItem(MinimaxModel):
    """`SAOP.API.Models.Item.ItemPriceListItem`"""

    title: str | None = Field(default=None, alias="Title")
    code: str | None = Field(default=None, alias="Code")
    price_without_vat: float | None = Field(default=None, alias="PriceWithoutVAT")
    price_with_vat: float | None = Field(default=None, alias="PriceWithVAT")
    unit_of_measurement: str | None = Field(default=None, alias="UnitOfMeasurement")
    item: FkField | None = Field(default=None, alias="Item")
    warehouse: FkField | None = Field(default=None, alias="Warehouse")
    customer: FkField | None = Field(default=None, alias="Customer")

class ItemSearch(MinimaxModel):
    """`SAOP.API.Models.Item.ItemSearch`"""

    item_id: int | None = Field(default=None, alias="ItemId")
    title: str | None = Field(default=None, alias="Title")
    code: str | None = Field(default=None, alias="Code")
    unit_of_measurement: str | None = Field(default=None, alias="UnitOfMeasurement")
    mass_per_unit: float | None = Field(default=None, alias="MassPerUnit")
    item_type: str | None = Field(default=None, alias="ItemType")
    vat_rate: FkField | None = Field(default=None, alias="VatRate")
    price: float | None = Field(default=None, alias="Price")
    currency: FkField | None = Field(default=None, alias="Currency")
    revenue_account_domestic: FkField | None = Field(default=None, alias="RevenueAccountDomestic")
    revenue_account_outside_eu: FkField | None = Field(
        default=None, alias="RevenueAccountOutsideEU"
    )
    revenue_account_eu: FkField | None = Field(default=None, alias="RevenueAccountEU")
    stocks_account: FkField | None = Field(default=None, alias="StocksAccount")
    composite: list[ItemComposite] | None = Field(default=None, alias="Composite")
    product_group: FkField | None = Field(default=None, alias="ProductGroup")
    classification_of_product_by_activity: FkField | None = Field(
        default=None, alias="ClassificationOfProductByActivity"
    )

class ItemsSettings(MinimaxModel):
    """`SAOP.API.Models.Item.ItemsSettings`"""

    prices_include_vat: str | None = Field(default=None, alias="PricesIncludeVAT")

class Journal(MinimaxModel):
    """`SAOP.API.Models.Journal.Journal`"""

    journal_id: int | None = Field(default=None, alias="JournalId")
    journal_type: FkField | None = Field(default=None, alias="JournalType")
    journal_date: str | None = Field(default=None, alias="JournalDate")
    description: str | None = Field(default=None, alias="Description")
    status: str | None = Field(default=None, alias="Status")
    journal_entries: list[JournalEntry] | None = Field(default=None, alias="JournalEntries")
    vat_entries: list[VATEntry] | None = Field(default=None, alias="VatEntries")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class JournalEntries(MinimaxModel):
    """`SAOP.API.Models.Journal.JournalEntries`"""

    journal_entry_id: int | None = Field(default=None, alias="JournalEntryId")
    journal: FkField | None = Field(default=None, alias="Journal")
    journal_type: FkField | None = Field(default=None, alias="JournalType")
    journal_date: str | None = Field(default=None, alias="JournalDate")
    journal_entry_date: str | None = Field(default=None, alias="JournalEntryDate")
    due_date: str | None = Field(default=None, alias="DueDate")
    transaction_date: str | None = Field(default=None, alias="TransactionDate")
    account: FkField | None = Field(default=None, alias="Account")
    customer: FkField | None = Field(default=None, alias="Customer")
    analytic: FkField | None = Field(default=None, alias="Analytic")
    employee: FkField | None = Field(default=None, alias="Employee")
    currency: FkField | None = Field(default=None, alias="Currency")
    description: str | None = Field(default=None, alias="Description")
    payment_reference: str | None = Field(default=None, alias="PaymentReference")
    debit: float | None = Field(default=None, alias="Debit")
    credit: float | None = Field(default=None, alias="Credit")
    debit_in_domestic_currency: float | None = Field(default=None, alias="DebitInDomesticCurrency")
    credit_in_domestic_currency: float | None = Field(
        default=None, alias="CreditInDomesticCurrency"
    )
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class JournalEntry(MinimaxModel):
    """`SAOP.API.Models.Journal.JournalEntry`"""

    external_id: str | None = Field(default=None, alias="ExternalId")
    journal_entry_id: int | None = Field(default=None, alias="JournalEntryId")
    journal: FkField | None = Field(default=None, alias="Journal")
    journal_entry_date: str | None = Field(default=None, alias="JournalEntryDate")
    due_date: str | None = Field(default=None, alias="DueDate")
    transaction_date: str | None = Field(default=None, alias="TransactionDate")
    account: FkField | None = Field(default=None, alias="Account")
    customer: FkField | None = Field(default=None, alias="Customer")
    analytic: FkField | None = Field(default=None, alias="Analytic")
    employee: FkField | None = Field(default=None, alias="Employee")
    currency: FkField | None = Field(default=None, alias="Currency")
    description: str | None = Field(default=None, alias="Description")
    payment_reference: str | None = Field(default=None, alias="PaymentReference")
    debit: float | None = Field(default=None, alias="Debit")
    credit: float | None = Field(default=None, alias="Credit")
    debit_in_domestic_currency: float | None = Field(default=None, alias="DebitInDomesticCurrency")
    credit_in_domestic_currency: float | None = Field(
        default=None, alias="CreditInDomesticCurrency"
    )
    submission_special_vat_return: str | None = Field(
        default=None, alias="SubmissionSpecialVATReturn"
    )
    vat_date: str | None = Field(default=None, alias="VatDate")
    vat_type: str | None = Field(default=None, alias="VatType")
    vat_rate_percentage: FkField | None = Field(default=None, alias="VatRatePercentage")
    vat_base_in_domestic_currency: float | None = Field(
        default=None, alias="VatBaseInDomesticCurrency"
    )
    vat_base: float | None = Field(default=None, alias="VatBase")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class JournalSearch(MinimaxModel):
    """`SAOP.API.Models.Journal.JournalSearch`"""

    journal_id: int | None = Field(default=None, alias="JournalId")
    journal_type: FkField | None = Field(default=None, alias="JournalType")
    journal_date: str | None = Field(default=None, alias="JournalDate")
    description: str | None = Field(default=None, alias="Description")

class VATEntry(MinimaxModel):
    """`SAOP.API.Models.Journal.VATEntry`"""

    vat_entry_id: int | None = Field(default=None, alias="VatEntryId")
    journal: FkField | None = Field(default=None, alias="Journal")
    vat_date: str | None = Field(default=None, alias="VatDate")
    vat_book: str | None = Field(default=None, alias="VatBook")
    vat_accounting_type: str | None = Field(default=None, alias="VatAccountingType")
    basis_for_correction: str | None = Field(default=None, alias="BasisForCorrection")
    forward_to_sef: str | None = Field(default=None, alias="ForwardToSEF")
    vat_entry_date: str | None = Field(default=None, alias="VatEntryDate")
    customer: FkField | None = Field(default=None, alias="Customer")
    document: str | None = Field(default=None, alias="Document")
    invoice_type: str | None = Field(default=None, alias="InvoiceType")
    document_date: str | None = Field(default=None, alias="DocumentDate")
    received_date: str | None = Field(default=None, alias="ReceivedDate")
    payment_date: str | None = Field(default=None, alias="PaymentDate")
    transaction_date: str | None = Field(default=None, alias="TransactionDate")
    date_approved: str | None = Field(default=None, alias="DateApproved")
    self_taxing: str | None = Field(default=None, alias="SelfTaxing")
    obj: str | None = Field(default=None, alias="OBJ")
    reverse: str | None = Field(default=None, alias="Reverse")
    self_taxing_related_document: str | None = Field(
        default=None, alias="SelfTaxingRelatedDocument"
    )
    journal_entry: FkField | None = Field(default=None, alias="JournalEntry")
    journal_entry_external_id: str | None = Field(default=None, alias="JournalEntryExternalId")
    notes: str | None = Field(default=None, alias="Notes")
    advance_payment: str | None = Field(default=None, alias="AdvancePayment")
    reporting_type: str | None = Field(default=None, alias="ReportingType")
    analytic: FkField | None = Field(default=None, alias="Analytic")
    vat_entry_rows: list[VATEntryRow] | None = Field(default=None, alias="VatEntryRows")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class VATEntryRow(MinimaxModel):
    """`SAOP.API.Models.Journal.VATEntryRow`"""

    vat_entry_row_id: int | None = Field(default=None, alias="VatEntryRowId")
    vat_entry: FkField | None = Field(default=None, alias="VatEntry")
    vat_rate: FkField | None = Field(default=None, alias="VatRate")
    vat_base: float | None = Field(default=None, alias="VatBase")
    vat: float | None = Field(default=None, alias="Vat")
    non_deductible_vat_base: float | None = Field(default=None, alias="NonDeductibleVatBase")
    non_deductible_vat: float | None = Field(default=None, alias="NonDeductibleVat")
    services_vat_base: float | None = Field(default=None, alias="ServicesVatBase")
    services_vat: float | None = Field(default=None, alias="ServicesVat")
    services_non_deductible_vat_base: float | None = Field(
        default=None, alias="ServicesNonDeductibleVatBase"
    )
    services_non_deductible_vat: float | None = Field(
        default=None, alias="ServicesNonDeductibleVat"
    )
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class JournalType(MinimaxModel):
    """`SAOP.API.Models.JournalType.JournalType`"""

    journal_type_id: int | None = Field(default=None, alias="JournalTypeId")
    code: str | None = Field(default=None, alias="Code")
    display_code: str | None = Field(default=None, alias="DisplayCode")

class ItemDataListResult(MinimaxModel):
    """`SAOP.API.Models.ListResult[SAOP.API.Models.Item.ItemData]`"""

    rows: list[ItemData] | None = Field(default=None, alias="Rows")
    validation_messages: list[mMApiValidationMessage] | None = Field(
        default=None, alias="ValidationMessages"
    )

class ItemPriceListItemListResult(MinimaxModel):
    """`SAOP.API.Models.ListResult[SAOP.API.Models.Item.ItemPriceListItem]`"""

    rows: list[ItemPriceListItem] | None = Field(default=None, alias="Rows")
    validation_messages: list[mMApiValidationMessage] | None = Field(
        default=None, alias="ValidationMessages"
    )

class Order(MinimaxModel):
    """`SAOP.API.Models.Order.Order`"""

    order_id: int | None = Field(default=None, alias="OrderId")
    received_issued: str | None = Field(default=None, alias="ReceivedIssued")
    year: int | None = Field(default=None, alias="Year")
    number: int | None = Field(default=None, alias="Number")
    date: str | None = Field(default=None, alias="Date")
    customer: FkField | None = Field(default=None, alias="Customer")
    customer_name: str | None = Field(default=None, alias="CustomerName")
    customer_address: str | None = Field(default=None, alias="CustomerAddress")
    customer_postal_code: str | None = Field(default=None, alias="CustomerPostalCode")
    customer_city: str | None = Field(default=None, alias="CustomerCity")
    customer_country: FkField | None = Field(default=None, alias="CustomerCountry")
    customer_country_name: str | None = Field(default=None, alias="CustomerCountryName")
    recipient_name: str | None = Field(default=None, alias="RecipientName")
    recipient_address: str | None = Field(default=None, alias="RecipientAddress")
    recipient_postal_code: str | None = Field(default=None, alias="RecipientPostalCode")
    recipient_city: str | None = Field(default=None, alias="RecipientCity")
    recipient_country_name: str | None = Field(default=None, alias="RecipientCountryName")
    recipient_country: FkField | None = Field(default=None, alias="RecipientCountry")
    analytic: FkField | None = Field(default=None, alias="Analytic")
    due_date: str | None = Field(default=None, alias="DueDate")
    reference: str | None = Field(default=None, alias="Reference")
    currency: FkField | None = Field(default=None, alias="Currency")
    notes: str | None = Field(default=None, alias="Notes")
    date_confirmed: str | None = Field(default=None, alias="DateConfirmed")
    date_completed: str | None = Field(default=None, alias="DateCompleted")
    date_canceled: str | None = Field(default=None, alias="DateCanceled")
    status: str | None = Field(default=None, alias="Status")
    description_above: str | None = Field(default=None, alias="DescriptionAbove")
    description_below: str | None = Field(default=None, alias="DescriptionBelow")
    report_template: FkField | None = Field(default=None, alias="ReportTemplate")
    order_rows: list[OrderRow] | None = Field(default=None, alias="OrderRows")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class OrderRow(MinimaxModel):
    """`SAOP.API.Models.Order.OrderRow`"""

    order_row_id: int | None = Field(default=None, alias="OrderRowId")
    order: FkField | None = Field(default=None, alias="Order")
    item: FkField | None = Field(default=None, alias="Item")
    warehouse: FkField | None = Field(default=None, alias="Warehouse")
    item_name: str | None = Field(default=None, alias="ItemName")
    item_code: str | None = Field(default=None, alias="ItemCode")
    description: str | None = Field(default=None, alias="Description")
    quantity: float | None = Field(default=None, alias="Quantity")
    discount_percent: float | None = Field(default=None, alias="DiscountPercent")
    price: float | None = Field(default=None, alias="Price")
    unit_of_measurement: str | None = Field(default=None, alias="UnitOfMeasurement")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class OrderSearch(MinimaxModel):
    """`SAOP.API.Models.Order.OrderSearch`"""

    order_id: int | None = Field(default=None, alias="OrderId")
    received_issued: str | None = Field(default=None, alias="ReceivedIssued")
    year: int | None = Field(default=None, alias="Year")
    number: int | None = Field(default=None, alias="Number")
    date: str | None = Field(default=None, alias="Date")
    customer: FkField | None = Field(default=None, alias="Customer")
    analytic: FkField | None = Field(default=None, alias="Analytic")
    currency: FkField | None = Field(default=None, alias="Currency")
    status: str | None = Field(default=None, alias="Status")

class Organisation(MinimaxModel):
    """`SAOP.API.Models.Organisation.Organisation`"""

    organisation_id: int | None = Field(default=None, alias="OrganisationId")
    title: str | None = Field(default=None, alias="Title")
    address: str | None = Field(default=None, alias="Address")
    postal_code: str | None = Field(default=None, alias="PostalCode")
    city: str | None = Field(default=None, alias="City")
    country: FkField | None = Field(default=None, alias="Country")
    tax_number: str | None = Field(default=None, alias="TaxNumber")
    registration_number: str | None = Field(default=None, alias="RegistrationNumber")
    vat_identification_number: str | None = Field(default=None, alias="VATIdentificationNumber")
    administrator: FkField | None = Field(default=None, alias="Administrator")
    status: str | None = Field(default=None, alias="Status")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class Outbox(MinimaxModel):
    """`SAOP.API.Models.Outbox.Outbox`"""

    outbox_id: int | None = Field(default=None, alias="OutboxId")
    customer: FkField | None = Field(default=None, alias="Customer")
    employee: FkField | None = Field(default=None, alias="Employee")
    outbox_date: str | None = Field(default=None, alias="OutboxDate")
    outbox_type: str | None = Field(default=None, alias="OutboxType")
    description: str | None = Field(default=None, alias="Description")
    attachments: list[OutboxAttachment] | None = Field(default=None, alias="Attachments")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class OutboxAttachment(MinimaxModel):
    """`SAOP.API.Models.Outbox.OutboxAttachment`"""

    outbox_attachment_id: int | None = Field(default=None, alias="OutboxAttachmentId")
    outbox: FkField | None = Field(default=None, alias="Outbox")
    attachment_data: str | None = Field(default=None, alias="AttachmentData")
    attachment_date: str | None = Field(default=None, alias="AttachmentDate")
    attachment_file_name: str | None = Field(default=None, alias="AttachmentFileName")
    attachment_mime_type: str | None = Field(default=None, alias="AttachmentMimeType")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class PaymentMethodPaymentMethodSearch(MinimaxModel):
    """`SAOP.API.Models.PaymentMethod.PaymentMethodSearch`"""

    payment_method_id: int | None = Field(default=None, alias="PaymentMethodId")
    name: str | None = Field(default=None, alias="Name")
    type_: str | None = Field(default=None, alias="Type")
    usage: str | None = Field(default=None, alias="Usage")
    default: str | None = Field(default=None, alias="Default")

class PayrollSettings(MinimaxModel):
    """`SAOP.API.Models.Payroll.PayrollSettings`"""

    payroll_settings_id: int | None = Field(default=None, alias="PayrollSettingsId")
    code: str | None = Field(default=None, alias="Code")
    name: str | None = Field(default=None, alias="Name")
    description: str | None = Field(default=None, alias="Description")
    customer_code: str | None = Field(default=None, alias="CustomerCode")
    customer_name: str | None = Field(default=None, alias="CustomerName")
    value: float | None = Field(default=None, alias="Value")
    date: str | None = Field(default=None, alias="Date")

class PostalCode(MinimaxModel):
    """`SAOP.API.Models.PostalCode.PostalCode`"""

    postal_code_id: int | None = Field(default=None, alias="PostalCodeId")
    code: str | None = Field(default=None, alias="Code")
    city: str | None = Field(default=None, alias="City")
    country: FkField | None = Field(default=None, alias="Country")

class ProductGroup(MinimaxModel):
    """`SAOP.API.Models.ProductGroup.ProductGroup`"""

    product_group_id: int | None = Field(default=None, alias="ProductGroupId")
    code: str | None = Field(default=None, alias="Code")
    name: str | None = Field(default=None, alias="Name")
    usage: str | None = Field(default=None, alias="Usage")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class PurposeCode(MinimaxModel):
    """`SAOP.API.Models.PurposeCode.PurposeCode`"""

    purpose_code_id: int | None = Field(default=None, alias="PurposeCodeId")
    code: str | None = Field(default=None, alias="Code")
    description: str | None = Field(default=None, alias="Description")

class EFakturaEntry(MinimaxModel):
    """`SAOP.API.Models.RSEFaktura.EFakturaEntry`"""

    registration_number: str | None = Field(default=None, alias="RegistrationNumber")
    budget_user_number: str | None = Field(default=None, alias="BudgetUserNumber")
    vat_identification_number: str | None = Field(default=None, alias="VatIdentificationNumber")
    name: str | None = Field(default=None, alias="Name")

class ReceivedInvoice(MinimaxModel):
    """`SAOP.API.Models.ReceivedInvoice.ReceivedInvoice`"""

    received_invoice_id: int | None = Field(default=None, alias="ReceivedInvoiceId")
    year: int | None = Field(default=None, alias="Year")
    invoice_number: int | None = Field(default=None, alias="InvoiceNumber")
    document_numbering: FkField | None = Field(default=None, alias="DocumentNumbering")
    document_reference: str | None = Field(default=None, alias="DocumentReference")
    customer: FkField | None = Field(default=None, alias="Customer")
    employee: FkField | None = Field(default=None, alias="Employee")
    analytic: FkField | None = Field(default=None, alias="Analytic")
    currency: FkField | None = Field(default=None, alias="Currency")
    date_issued: str | None = Field(default=None, alias="DateIssued")
    date_transaction: str | None = Field(default=None, alias="DateTransaction")
    date_due: str | None = Field(default=None, alias="DateDue")
    date_received: str | None = Field(default=None, alias="DateReceived")
    date_approved: str | None = Field(default=None, alias="DateApproved")
    invoice_amount: float | None = Field(default=None, alias="InvoiceAmount")
    invoice_amount_domestic_currency: float | None = Field(
        default=None, alias="InvoiceAmountDomesticCurrency"
    )
    status: str | None = Field(default=None, alias="Status")
    bank_account: FkField | None = Field(default=None, alias="BankAccount")
    payment_reference_type: str | None = Field(default=None, alias="PaymentReferenceType")
    payment_reference_model: str | None = Field(default=None, alias="PaymentReferenceModel")
    payment_reference_number: str | None = Field(default=None, alias="PaymentReferenceNumber")
    notes: str | None = Field(default=None, alias="Notes")
    payment_type: str | None = Field(default=None, alias="PaymentType")
    revenue_expense: FkField | None = Field(default=None, alias="RevenueExpense")
    cash_register: FkField | None = Field(default=None, alias="CashRegister")
    date_expense: str | None = Field(default=None, alias="DateExpense")
    recurring_invoice: str | None = Field(default=None, alias="RecurringInvoice")
    payment_status: str | None = Field(default=None, alias="PaymentStatus")
    invoice_value: float | None = Field(default=None, alias="InvoiceValue")
    paid_value: float | None = Field(default=None, alias="PaidValue")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class ReceivedInvoiceSearch(MinimaxModel):
    """`SAOP.API.Models.ReceivedInvoice.ReceivedInvoiceSearch`"""

    received_invoice_id: int | None = Field(default=None, alias="ReceivedInvoiceId")
    year: int | None = Field(default=None, alias="Year")
    invoice_number: int | None = Field(default=None, alias="InvoiceNumber")
    document_numbering: FkField | None = Field(default=None, alias="DocumentNumbering")
    document_reference: str | None = Field(default=None, alias="DocumentReference")
    customer: FkField | None = Field(default=None, alias="Customer")
    analytic: FkField | None = Field(default=None, alias="Analytic")
    currency: FkField | None = Field(default=None, alias="Currency")
    date_issued: str | None = Field(default=None, alias="DateIssued")
    date_transaction: str | None = Field(default=None, alias="DateTransaction")
    date_due: str | None = Field(default=None, alias="DateDue")
    date_received: str | None = Field(default=None, alias="DateReceived")
    invoice_amount: float | None = Field(default=None, alias="InvoiceAmount")
    status: str | None = Field(default=None, alias="Status")
    payment_status: str | None = Field(default=None, alias="PaymentStatus")
    invoice_value: float | None = Field(default=None, alias="InvoiceValue")
    paid_value: float | None = Field(default=None, alias="PaidValue")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class ReportTemplate(MinimaxModel):
    """`SAOP.API.Models.ReportTemplate.ReportTemplate`"""

    report_template_id: int | None = Field(default=None, alias="ReportTemplateId")
    name: str | None = Field(default=None, alias="Name")
    display_type: str | None = Field(default=None, alias="DisplayType")
    default: str | None = Field(default=None, alias="Default")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class StockEntry(MinimaxModel):
    """`SAOP.API.Models.Stock.StockEntry`"""

    stock_entry_id: int | None = Field(default=None, alias="StockEntryId")
    stock_entry_type: str | None = Field(default=None, alias="StockEntryType")
    stock_entry_subtype: str | None = Field(default=None, alias="StockEntrySubtype")
    receipt_from_farmer: str | None = Field(default=None, alias="ReceiptFromFarmer")
    date: str | None = Field(default=None, alias="Date")
    number: int | None = Field(default=None, alias="Number")
    customer: FkField | None = Field(default=None, alias="Customer")
    analytic: FkField | None = Field(default=None, alias="Analytic")
    rabate: float | None = Field(default=None, alias="Rabate")
    description: str | None = Field(default=None, alias="Description")
    value_of_material_and_goods: float | None = Field(default=None, alias="ValueOfMaterialAndGoods")
    value_of_related_costs: float | None = Field(default=None, alias="ValueOfRelatedCosts")
    percent_of_direct_costs_of_purchase: float | None = Field(
        default=None, alias="PercentOfDirectCostsOfPurchase"
    )
    value_of_receipt: float | None = Field(default=None, alias="ValueOfReceipt")
    currency: FkField | None = Field(default=None, alias="Currency")
    exchange_rate: float | None = Field(default=None, alias="ExchangeRate")
    original_document_type: str | None = Field(default=None, alias="OriginalDocumentType")
    original_document_date: str | None = Field(default=None, alias="OriginalDocumentDate")
    delivery_note_report_template: FkField | None = Field(
        default=None, alias="DeliveryNoteReportTemplate"
    )
    delivery_note_description_above: str | None = Field(
        default=None, alias="DeliveryNoteDescriptionAbove"
    )
    delivery_note_description_below: str | None = Field(
        default=None, alias="DeliveryNoteDescriptionBelow"
    )
    addressee_name: str | None = Field(default=None, alias="AddresseeName")
    addressee_gln: str | None = Field(default=None, alias="AddresseeGLN")
    addressee_address: str | None = Field(default=None, alias="AddresseeAddress")
    addressee_postal_code: str | None = Field(default=None, alias="AddresseePostalCode")
    addressee_city: str | None = Field(default=None, alias="AddresseeCity")
    addressee_country_name: str | None = Field(default=None, alias="AddresseeCountryName")
    addressee_country: FkField | None = Field(default=None, alias="AddresseeCountry")
    recipient_name: str | None = Field(default=None, alias="RecipientName")
    recipient_gln: str | None = Field(default=None, alias="RecipientGLN")
    recipient_address: str | None = Field(default=None, alias="RecipientAddress")
    recipient_postal_code: str | None = Field(default=None, alias="RecipientPostalCode")
    recipient_city: str | None = Field(default=None, alias="RecipientCity")
    recipient_country_name: str | None = Field(default=None, alias="RecipientCountryName")
    recipient_country: FkField | None = Field(default=None, alias="RecipientCountry")
    status: str | None = Field(default=None, alias="Status")
    account: FkField | None = Field(default=None, alias="Account")
    association_with_issued_invoice: str | None = Field(
        default=None, alias="AssociationWithIssuedInvoice"
    )
    stock_entry_rows: list[StockEntryRow] | None = Field(default=None, alias="StockEntryRows")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class StockEntryRow(MinimaxModel):
    """`SAOP.API.Models.Stock.StockEntryRow`"""

    stock_entry_row_id: int | None = Field(default=None, alias="StockEntryRowId")
    stock_entry: FkField | None = Field(default=None, alias="StockEntry")
    row_number: int | None = Field(default=None, alias="RowNumber")
    item: FkField | None = Field(default=None, alias="Item")
    item_name: str | None = Field(default=None, alias="ItemName")
    warehouse_from: FkField | None = Field(default=None, alias="WarehouseFrom")
    warehouse_to: FkField | None = Field(default=None, alias="WarehouseTo")
    quantity: float | None = Field(default=None, alias="Quantity")
    price: float | None = Field(default=None, alias="Price")
    discount_percent: float | None = Field(default=None, alias="DiscountPercent")
    linked_stock_entry_row: FkField | None = Field(default=None, alias="LinkedStockEntryRow")
    margin_percent: float | None = Field(default=None, alias="MarginPercent")
    selling_price: float | None = Field(default=None, alias="SellingPrice")
    selling_price_includes_vat: str | None = Field(default=None, alias="SellingPriceIncludesVAT")
    value: float | None = Field(default=None, alias="Value")
    serial_number: str | None = Field(default=None, alias="SerialNumber")
    batch_number: str | None = Field(default=None, alias="BatchNumber")
    mass: float | None = Field(default=None, alias="Mass")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class StockEntrySearch(MinimaxModel):
    """`SAOP.API.Models.Stock.StockEntrySearch`"""

    stock_entry_id: int | None = Field(default=None, alias="StockEntryId")
    stock_entry_type: str | None = Field(default=None, alias="StockEntryType")
    stock_entry_subtype: str | None = Field(default=None, alias="StockEntrySubtype")
    date: str | None = Field(default=None, alias="Date")
    number: int | None = Field(default=None, alias="Number")
    customer: FkField | None = Field(default=None, alias="Customer")
    analytic: FkField | None = Field(default=None, alias="Analytic")
    status: str | None = Field(default=None, alias="Status")

class StockListItem(MinimaxModel):
    """`SAOP.API.Models.Stock.StockListItem`"""

    item: FkField | None = Field(default=None, alias="Item")
    item_name: str | None = Field(default=None, alias="ItemName")
    item_code: str | None = Field(default=None, alias="ItemCode")
    item_ean_code: str | None = Field(default=None, alias="ItemEANCode")
    unit_of_measurement: str | None = Field(default=None, alias="UnitOfMeasurement")
    average_purchase_price: float | None = Field(default=None, alias="AveragePurchasePrice")
    selling_price: float | None = Field(default=None, alias="SellingPrice")
    quantity: float | None = Field(default=None, alias="Quantity")
    value: float | None = Field(default=None, alias="Value")
    batch_number: str | None = Field(default=None, alias="BatchNumber")
    currency: FkField | None = Field(default=None, alias="Currency")

class SyncCandidate(MinimaxModel):
    """`SAOP.API.Models.SyncCandidate`"""

    id: int | None = Field(default=None, alias="ID")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

class SyncQueryResult(MinimaxModel):
    """`SAOP.API.Models.SyncQueryResult[SAOP.API.Models.SyncCandidate]`"""

    rows: list[SyncCandidate] | None = Field(default=None, alias="Rows")
    total_rows: int | None = Field(default=None, alias="TotalRows")
    current_page_number: int | None = Field(default=None, alias="CurrentPageNumber")
    page_size: int | None = Field(default=None, alias="PageSize")

class User(MinimaxModel):
    """`SAOP.API.Models.User.User`"""

    user_id: int | None = Field(default=None, alias="UserId")
    full_name: str | None = Field(default=None, alias="FullName")
    email: str | None = Field(default=None, alias="Email")
    mobile_phone: str | None = Field(default=None, alias="MobilePhone")
    language: str | None = Field(default=None, alias="Language")

class UserOrganisation(MinimaxModel):
    """`SAOP.API.Models.User.UserOrganisation`"""

    organisation: FkField | None = Field(default=None, alias="Organisation")
    api_access: str | None = Field(default=None, alias="APIAccess")
    mobile_access: str | None = Field(default=None, alias="MobileAccess")

class VatAccountingType(MinimaxModel):
    """`SAOP.API.Models.VatAccountingType.VatAccountingType`"""

    code: str | None = Field(default=None, alias="Code")
    issued_recived: str | None = Field(default=None, alias="IssuedRecived")
    valid_from: str | None = Field(default=None, alias="ValidFrom")
    valid_to: str | None = Field(default=None, alias="ValidTo")
    name: str | None = Field(default=None, alias="Name")

class VatRate(MinimaxModel):
    """`SAOP.API.Models.VatRate.VatRate`"""

    vat_rate_id: int | None = Field(default=None, alias="VatRateId")
    code: str | None = Field(default=None, alias="Code")
    percent: float | None = Field(default=None, alias="Percent")
    vat_rate_percentage: FkField | None = Field(default=None, alias="VatRatePercentage")

class Warehouse(MinimaxModel):
    """`SAOP.API.Models.Warehouse.Warehouse`"""

    warehouse_id: int | None = Field(default=None, alias="WarehouseId")
    code: str | None = Field(default=None, alias="Code")
    name: str | None = Field(default=None, alias="Name")
    location: str | None = Field(default=None, alias="Location")
    inventory_management: str | None = Field(default=None, alias="InventoryManagement")
    inventory_management_by_value: str | None = Field(
        default=None, alias="InventoryManagementByValue"
    )
    selling_price_input: str | None = Field(default=None, alias="SellingPriceInput")
    inventory_bookkeping: str | None = Field(default=None, alias="InventoryBookkeping")
    stocks_account: FkField | None = Field(default=None, alias="StocksAccount")
    pd_account: FkField | None = Field(default=None, alias="PDAccount")
    vat_standard_account: FkField | None = Field(default=None, alias="VATStandardAccount")
    vat_reduced_account: FkField | None = Field(default=None, alias="VATReducedAccount")
    vat_special_reduced_account: FkField | None = Field(
        default=None, alias="VATSpecialReducedAccount"
    )
    usage: str | None = Field(default=None, alias="Usage")
    record_dt_modified: str | None = Field(default=None, alias="RecordDtModified")
    row_version: str | None = Field(default=None, alias="RowVersion")

FkField.model_rebuild()
mMApiValidationMessage.model_rebuild()
Account.model_rebuild()
AddressModel.model_rebuild()
Analytic.model_rebuild()
AnalyticSearch.model_rebuild()
Attachment.model_rebuild()
BankAccount.model_rebuild()
ClassificationOfProductByActivity.model_rebuild()
Contact.model_rebuild()
Country.model_rebuild()
Currency.model_rebuild()
Customer.model_rebuild()
CustomerSearch.model_rebuild()
AgregateInvoice.model_rebuild()
AgregateInvoiceChart.model_rebuild()
DashboardCustomerChart.model_rebuild()
DashboardMonthChart.model_rebuild()
Dashboard.model_rebuild()
DashboardCustomer.model_rebuild()
DashboardMonth.model_rebuild()
AttachmentLink.model_rebuild()
Document.model_rebuild()
DocumentAttachment.model_rebuild()
DocumentSearch.model_rebuild()
DocumentNumbering.model_rebuild()
Employee.model_rebuild()
EmployeeSearch.model_rebuild()
ExchangeRate.model_rebuild()
Inbox.model_rebuild()
InboxAttachment.model_rebuild()
IssuedInvoice.model_rebuild()
IssuedInvoiceAdditionalSourceDocument.model_rebuild()
IssuedInvoicePaymentMethod.model_rebuild()
IssuedInvoiceRow.model_rebuild()
IssuedInvoiceSearch.model_rebuild()
IssuedInvoicePaymentMethodSearch.model_rebuild()
IssuedInvoicePosting.model_rebuild()
IssuedInvoicePostingPaymentMethod.model_rebuild()
IssuedInvoicePostingRetailDataForBookkeeping.model_rebuild()
IssuedInvoicePostingRetailDataForBookkeepingRow.model_rebuild()
IssuedInvoicePostingRetailDataForStockManagement.model_rebuild()
IssuedInvoicePostingRetailDataForStockManagementRow.model_rebuild()
IssuedInvoicePostingRetailDataForValueBasedStockManagement.model_rebuild()
IssuedInvoicePostingRetailDataForValueBasedStockManagementRow.model_rebuild()
IssuedInvoicePostingRevenue.model_rebuild()
IssuedInvoicePostingSearch.model_rebuild()
IssuedInvoicePostingTax.model_rebuild()
IssuedInvoicePostingPaymentMethodSearch.model_rebuild()
Item.model_rebuild()
ItemComposite.model_rebuild()
ItemData.model_rebuild()
ItemPriceListItem.model_rebuild()
ItemSearch.model_rebuild()
ItemsSettings.model_rebuild()
Journal.model_rebuild()
JournalEntries.model_rebuild()
JournalEntry.model_rebuild()
JournalSearch.model_rebuild()
VATEntry.model_rebuild()
VATEntryRow.model_rebuild()
JournalType.model_rebuild()
ItemDataListResult.model_rebuild()
ItemPriceListItemListResult.model_rebuild()
Order.model_rebuild()
OrderRow.model_rebuild()
OrderSearch.model_rebuild()
Organisation.model_rebuild()
Outbox.model_rebuild()
OutboxAttachment.model_rebuild()
PaymentMethodPaymentMethodSearch.model_rebuild()
PayrollSettings.model_rebuild()
PostalCode.model_rebuild()
ProductGroup.model_rebuild()
PurposeCode.model_rebuild()
EFakturaEntry.model_rebuild()
ReceivedInvoice.model_rebuild()
ReceivedInvoiceSearch.model_rebuild()
ReportTemplate.model_rebuild()
StockEntry.model_rebuild()
StockEntryRow.model_rebuild()
StockEntrySearch.model_rebuild()
StockListItem.model_rebuild()
SyncCandidate.model_rebuild()
SyncQueryResult.model_rebuild()
User.model_rebuild()
UserOrganisation.model_rebuild()
VatAccountingType.model_rebuild()
VatRate.model_rebuild()
Warehouse.model_rebuild()
