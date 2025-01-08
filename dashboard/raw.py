def tenant_dashboard(request):
    """Dashboard view for cross-tenant users showing all their leased units across different clients"""
    if not request.user.is_authenticated:
        return redirect('login')
        
    context = {}
    
    try:
        shared_id = request.user.tenant_profile.shared_id
        all_leased_units = []
        all_leases = []
        
        # Get all leased units across clients
        clients = Client.objects.all()
        for client in clients:
            try:
                with schema_context(client.schema_name):
                    units = Unit.objects.filter(tenant_id=shared_id)
                    leases = Lease.objects.filter(tenant_shared_id=shared_id)
                    
                    # Add client context to each unit and lease
                    for unit in units:
                        unit.client_name = client.name
                        unit.schema_name = client.schema_name
                    
                    for lease in leases:
                        lease.client_name = client.name
                        lease.schema_name = client.schema_name
                        lease.days_remaining = calculate_days_difference(
                            timezone.now().date(), 
                            lease.end_date
                        )
                    
                    all_leased_units.extend(units)
                    all_leases.extend(leases)
            except Exception as e:
                # Log the error but continue processing other clients
                logger.error(f"Error processing client {client.name}: {str(e)}")
                continue
        
        context.update({
            'shared_id': shared_id,
            'leased_units': all_leased_units,
            'leases': all_leases,
            'total_units': len(all_leased_units),
            'total_leases': len(all_leases),
        })
        
    except AttributeError:
        # Handle case where user doesn't have a tenant profile
        messages.error(request, "No tenant profile found. Please contact support.")
    except Exception as e:
        # Log unexpected errors
        logger.error(f"Unexpected error in tenant dashboard: {str(e)}")
        messages.error(request, "An error occurred while loading your dashboard.")
    
    return render(request, 'tenant_dashboard.html', context)




def tenant_dashboard(request):
    """Dashboard view for cross-tenant users showing all their leased units across different clients"""
    if not request.user.is_authenticated:
        return redirect('login')
        
    context = {}
    
    try:
        shared_id = request.user.tenant_profile.shared_id
        selected_client = request.GET.get('client', None)
        all_leased_units = []
        all_leases = []
        
        # Get all clients and their units/leases
        clients = Client.objects.all()
        clients_data = []
        
        for client in clients:
            try:
                # Query units and leases for this client
                leased_units = query_schema_all(client.schema_name, Unit).filter(tenant_id=shared_id)
                leases = query_schema_all(client.schema_name, Lease).filter(tenant_shared_id=shared_id)
                
                if leased_units.exists():  # Only add client if tenant has units
                    client_data = {
                        'client': client,
                        'units': [],
                        'leases': []
                    }
                    
                    # Process units
                    for unit in leased_units:
                        unit_data = {
                            'unit': unit,
                            'client_name': client.name,
                            'schema_name': client.schema_name
                        }
                        client_data['units'].append(unit_data)
                        all_leased_units.append(unit_data)
                    
                    # Process leases
                    for lease in leases:
                        lease_data = {
                            'lease': lease,
                            'client_name': client.name,
                            'schema_name': client.schema_name,
                            'days_remaining': calculate_days_difference(
                                timezone.now().date(), 
                                lease.end_date
                            )
                        }
                        client_data['leases'].append(lease_data)
                        all_leases.append(lease_data)
                    
                    clients_data.append(client_data)
                    
            except Exception as e:
                logger.error(f"Error processing client {client.name}: {str(e)}")
                messages.error(
                    request, 
                    f"Unable to load data for {client.name}. Please try again later."
                )
                continue
        
        # Handle client selection
        if selected_client:
            selected_client_data = next(
                (cd for cd in clients_data if cd['client'].id == int(selected_client)), 
                None
            )
            if selected_client_data:
                context['selected_units'] = selected_client_data['units']
                context['selected_leases'] = selected_client_data['leases']
            else:
                messages.warning(request, "Selected client not found or no units available.")
        
        # Add all data to context
        context.update({
            'shared_id': shared_id,
            'clients_data': clients_data,
            'all_leased_units': all_leased_units,
            'all_leases': all_leases,
            'total_units': len(all_leased_units),
            'total_leases': len(all_leases),
            'selected_client': selected_client
        })
        
    except AttributeError:
        messages.error(
            request, 
            "No tenant profile found. Please contact support."
        )
        logger.error(f"No tenant profile found for user {request.user.id}")
    except Exception as e:
        messages.error(
            request, 
            "An error occurred while loading your dashboard."
        )
        logger.error(f"Unexpected error in tenant dashboard: {str(e)}")
    
    return render(request, 'tenant_dashboard.html', context)