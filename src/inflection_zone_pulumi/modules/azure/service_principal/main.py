import pulumi_azuread as azuread

# Create an AD service principal
ad_app = azuread.Application("aks", display_name="aks")
ad_sp = azuread.ServicePrincipal("aksSp", application_id=ad_app.application_id)

# Create the Service Principal Password
ad_sp_password = azuread.ServicePrincipalPassword("aksSpPassword",
                                                  service_principal_id=ad_sp.id,
                                                  end_date="2099-01-01T00:00:00Z")