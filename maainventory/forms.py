from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from decimal import Decimal
from .models import UserProfile, Role, Branch, BranchUser, Brand, ValidPunchID, Supplier, SupplierCategory, Item, SupplierItem, ItemVariation, BaseUnit, ItemPhoto, SupplierPriceDiscussion


class RegistrationForm(UserCreationForm):
    """Registration form that extends UserCreationForm with full_name, punch_id, role, brand, and branches"""
    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=255, required=True, label='Full Name')
    punch_id = forms.CharField(max_length=100, required=True, label='Punch ID', help_text='Enter your employee Punch ID')
    
    def clean_punch_id(self):
        punch_id = self.cleaned_data.get('punch_id')
        if punch_id:
            # Check if punch_id already exists in UserProfile
            if UserProfile.objects.filter(punch_id=punch_id).exists():
                raise forms.ValidationError('This Punch ID is already registered. Please use a different one.')
            
            # Check if punch_id is in the valid/approved list
            valid_punch_id = ValidPunchID.objects.filter(
                punch_id=punch_id,
                is_active=True
            ).first()
            
            if not valid_punch_id:
                raise forms.ValidationError(
                    'This Punch ID is not approved. Please contact IT to add your Punch ID to the system, '
                    'or use a valid Punch ID from the approved list.'
                )
        return punch_id
    role = forms.ModelChoiceField(
        queryset=Role.objects.all(),
        required=False,
        empty_label='Select a role (optional)'
    )
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.all().order_by('name'),
        required=False,
        empty_label='Select a brand (optional)',
        label='Brand',
        help_text='Select a brand to see its branches'
    )
    branches = forms.ModelMultipleChoiceField(
        queryset=Branch.objects.none(),  # Will be filtered by JavaScript based on brand
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Branches',
        help_text='Select one or more branches you belong to (optional)'
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'full_name', 'punch_id', 'role', 'brand', 'branches', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Update branches queryset to include all active branches for validation
        # This allows the form to accept branch IDs submitted via JavaScript
        self.fields['branches'].queryset = Branch.objects.filter(is_active=True)
        
        # Style the form fields
        self.fields['username'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Enter username'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Enter email address'
        })
        self.fields['full_name'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Enter your full name'
        })
        self.fields['punch_id'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Enter your Punch ID'
        })
        self.fields['role'].widget.attrs.update({
            'class': 'form-select'
        })
        self.fields['brand'].widget.attrs.update({
            'class': 'form-select',
            'id': 'id_brand'
        })
        self.fields['branches'].widget.attrs.update({
            'id': 'id_branches'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Enter password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Confirm password'
        })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            # Save User to database
            user.save()
            # Create and save UserProfile to database
            UserProfile.objects.create(
                user=user,
                full_name=self.cleaned_data['full_name'],
                punch_id=self.cleaned_data['punch_id'],
                role=self.cleaned_data.get('role')
            )
            # Create BranchUser entries for selected branches
            branches = self.cleaned_data.get('branches', [])
            for branch in branches:
                BranchUser.objects.get_or_create(
                    user=user,
                    branch=branch
                )
        return user


class LoginForm(forms.Form):
    """Custom login form using email instead of username"""
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter email'
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Enter password'
        })
    )


class SupplierForm(forms.ModelForm):
    """Form for adding/editing suppliers"""
    
    DAYS_OF_WEEK = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]
    
    class Meta:
        model = Supplier
        fields = ['name', 'email', 'phone', 'address', 'category', 'contact_person', 'delivery_days', 'order_days', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter supplier name'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Enter email address'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter phone number'}),
            'address': forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Enter address (optional)', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-input', 'placeholder': 'Select category'}),
            'contact_person': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter contact person name'}),
            'delivery_days': forms.HiddenInput(),  # Hidden, will be set from checkbox selection and cutoff times
            'order_days': forms.HiddenInput(),  # Hidden, will be set from checkbox selection and cutoff times
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
        labels = {
            'name': 'Supplier Name',
            'email': 'Email',
            'phone': 'Phone',
            'address': 'Address',
            'category': 'Category',
            'contact_person': 'Contact Person',
            'delivery_days': 'Delivery Days',
            'order_days': 'Order Days',
            'is_active': 'Active',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set queryset for category field to only show active categories
        self.fields['category'].queryset = SupplierCategory.objects.filter(is_active=True).order_by('name')
        self.fields['name'].required = True
        self.fields['email'].required = True
        self.fields['phone'].required = True
        self.fields['category'].required = False  # Make it optional for now
        self.fields['delivery_days'].required = False  # Hidden field
        self.fields['order_days'].required = False  # Hidden field
        self.fields['address'].required = False
        self.fields['contact_person'].required = True
        
        # Add cutoff time fields for each day (initially hidden)
        for day, day_label in self.DAYS_OF_WEEK:
            field_name = f'cutoff_{day.lower()}'
            self.fields[field_name] = forms.TimeField(
                required=False,
                label=f'{day_label} Cutoff Time',
                widget=forms.TimeInput(attrs={
                    'class': 'form-input cutoff-time-input',
                    'type': 'time',
                    'data-day': day,
                })
            )
        
        # Add cutoff time fields for order days (initially hidden)
        for day, day_label in self.DAYS_OF_WEEK:
            field_name = f'order_cutoff_{day.lower()}'
            self.fields[field_name] = forms.TimeField(
                required=False,
                label=f'{day_label} Cutoff Time',
                widget=forms.TimeInput(attrs={
                    'class': 'form-input cutoff-time-input',
                    'type': 'time',
                    'data-day': day,
                })
            )
        
        # If editing and form is not bound (GET request), populate existing delivery days
        if not self.is_bound and self.instance and self.instance.pk and self.instance.delivery_days:
            if isinstance(self.instance.delivery_days, dict):
                for day, cutoff_time in self.instance.delivery_days.items():
                    field_name = f'cutoff_{day.lower()}'
                    if field_name in self.fields and isinstance(cutoff_time, str):
                        try:
                            from datetime import datetime
                            time_obj = datetime.strptime(cutoff_time, '%H:%M').time()
                            self.fields[field_name].initial = time_obj
                            self.fields[field_name].widget.attrs['style'] = 'display: block;'
                        except:
                            pass
        
        # Populate existing order days when editing (GET request only)
        if not self.is_bound and self.instance and self.instance.pk and self.instance.order_days:
            if isinstance(self.instance.order_days, dict):
                for day, cutoff_time in self.instance.order_days.items():
                    field_name = f'order_cutoff_{day.lower()}'
                    if field_name in self.fields and isinstance(cutoff_time, str):
                        try:
                            from datetime import datetime
                            time_obj = datetime.strptime(cutoff_time, '%H:%M').time()
                            self.fields[field_name].initial = time_obj
                            self.fields[field_name].widget.attrs['style'] = 'display: block;'
                        except:
                            pass
    
    def clean(self):
        cleaned_data = super().clean()
        delivery_days_dict = {}
        order_days_dict = {}
        
        # Process delivery days
        for day, day_label in self.DAYS_OF_WEEK:
            field_name = f'cutoff_{day.lower()}'
            day_checkbox_name = f'day_{day.lower()}'
            checkbox_checked = self.data.get(day_checkbox_name) == 'on'
            cutoff_time = cleaned_data.get(field_name)
            
            if checkbox_checked:
                if not cutoff_time:
                    raise forms.ValidationError(f'Please set delivery cutoff time for {day_label}.')
                delivery_days_dict[day] = cutoff_time.strftime('%H:%M')
        
        # Process order days
        for day, day_label in self.DAYS_OF_WEEK:
            field_name = f'order_cutoff_{day.lower()}'
            day_checkbox_name = f'order_day_{day.lower()}'
            checkbox_checked = self.data.get(day_checkbox_name) == 'on'
            cutoff_time = cleaned_data.get(field_name)
            
            if checkbox_checked:
                if not cutoff_time:
                    raise forms.ValidationError(f'Please set order cutoff time for {day_label}.')
                order_days_dict[day] = cutoff_time.strftime('%H:%M')
        
        # Delivery days is optional, so no validation error if empty
        cleaned_data['delivery_days'] = delivery_days_dict
        cleaned_data['order_days'] = order_days_dict
        return cleaned_data


class ItemForm(forms.ModelForm):
    """Form for adding/editing items"""
    
    class Meta:
        model = Item
        fields = ['item_code', 'name', 'description', 'brand', 'base_unit', 'min_order_qty', 'min_stock_qty', 'price_per_unit', 'notes']
        widgets = {
            'item_code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter item code'}),
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Enter item name'}),
            'description': forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Enter description (optional)', 'rows': 3}),
            'brand': forms.Select(attrs={'class': 'form-input', 'placeholder': 'Select brand'}),
            'base_unit': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g., pcs, kg, box'}),
            'min_order_qty': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Minimum order quantity', 'step': '0.01', 'min': '0'}),
            'min_stock_qty': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Minimum stock quantity', 'step': '0.01', 'min': '0'}),
            'price_per_unit': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Price per unit (optional)', 'step': '0.01', 'min': '0'}),
            'notes': forms.Textarea(attrs={'class': 'form-input', 'placeholder': 'Additional notes (optional)', 'rows': 3}),
        }
        labels = {
            'item_code': 'Item Code',
            'name': 'Item Name',
            'description': 'Description',
            'brand': 'Brand',
            'base_unit': 'Base Unit',
            'min_order_qty': 'Minimum Order Quantity',
            'min_stock_qty': 'Minimum Stock Quantity',
            'price_per_unit': 'Price per Unit',
            'notes': 'Notes',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['item_code'].required = True
        self.fields['name'].required = True
        self.fields['brand'].required = True
        self.fields['base_unit'].required = True
        self.fields['min_order_qty'].required = True
        self.fields['min_stock_qty'].required = True
        self.fields['description'].required = False
        self.fields['price_per_unit'].required = False
        self.fields['notes'].required = False
        # Set queryset for brand field
        self.fields['brand'].queryset = Brand.objects.all().order_by('name')

    def clean_min_order_qty(self):
        value = self.cleaned_data.get('min_order_qty')
        if value is None or value == 0:
            raise forms.ValidationError('This field is required and must be greater than 0.')
        return value

    def clean_min_stock_qty(self):
        value = self.cleaned_data.get('min_stock_qty')
        if value is None or value == 0:
            raise forms.ValidationError('This field is required and must be greater than 0.')
        return value


class SupplierItemForm(forms.ModelForm):
    """Form for adding/editing supplier items"""
    item_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Type item name',
            'autocomplete': 'off'
        }),
        label='Item Name',
        help_text='Enter the name for the new item'
    )
    item_code = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'readonly': True,
            'style': 'background-color: #f3f4f6; cursor: not-allowed;',
            'placeholder': 'Auto-generated'
        }),
        label='Item Code',
        help_text='Auto-generated based on supplier category'
    )
    item_min_stock_qty = forms.DecimalField(
        required=True,
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'step': '0.01',
            'min': '0',
            'placeholder': 'Minimum stock quantity'
        }),
        label='Item Min Stock Qty',
        help_text='Minimum stock quantity for this item'
    )
    
    class Meta:
        model = SupplierItem
        fields = ['supplier', 'base_unit', 'price_per_unit', 'min_order_qty', 'is_active']
        # Note: item_code is NOT in fields because it's auto-generated in save() method
        widgets = {
            'supplier': forms.Select(attrs={'class': 'form-input', 'placeholder': 'Select supplier', 'disabled': True, 'style': 'pointer-events: none; background-color: #f3f4f6; cursor: not-allowed;'}),
            'base_unit': forms.Select(attrs={'class': 'form-input', 'placeholder': 'Select base unit'}),
            'price_per_unit': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Price per unit', 'step': '0.01', 'min': '0'}),
            'min_order_qty': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Minimum order quantity', 'step': '0.01', 'min': '0'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }
        labels = {
            'supplier': 'Supplier',
            'base_unit': 'Base Unit',
            'price_per_unit': 'Price per Unit',
            'min_order_qty': 'Minimum Order Quantity',
            'is_active': 'Active',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['supplier'].required = True
        self.fields['base_unit'].required = True
        self.fields['price_per_unit'].required = True
        self.fields['min_order_qty'].required = True
        # Set querysets
        self.fields['supplier'].queryset = Supplier.objects.filter(is_active=True).order_by('name')
        base_units = BaseUnit.objects.filter(is_active=True).order_by('name')
        self.fields['base_unit'].queryset = base_units
        
        # Remove empty option (no "--------" option)
        self.fields['base_unit'].empty_label = None
        
        # Set default to first base unit if not editing and no value is set
        if not self.instance or not self.instance.pk:
            first_base_unit = base_units.first()
            if first_base_unit:
                self.fields['base_unit'].initial = first_base_unit.id
        
        # If editing, populate item_name, item_code fields
        if self.instance and self.instance.pk:
            if self.instance.item:
                self.fields['item_name'].initial = self.instance.item.name
                self.fields['item_min_stock_qty'].initial = self.instance.item.min_stock_qty
            if self.instance.item_code:
                self.fields['item_code'].initial = self.instance.item_code
        else:
            # For new items, show placeholder that it will be auto-generated
            self.fields['item_code'].initial = 'Auto-generated after saving'
    
    def clean_item_name(self):
        """Validate item name - check if it already exists"""
        item_name = self.cleaned_data.get('item_name', '').strip()
        if not item_name:
            raise forms.ValidationError('Item name is required.')
        
        # Check if item with this name already exists
        if Item.objects.filter(name__iexact=item_name, is_active=True).exists():
            raise forms.ValidationError(f'Item with name "{item_name}" already exists. Please use a different name.')
        
        return item_name
    
    def clean(self):
        """Validate the entire form"""
        cleaned_data = super().clean()
        
        # Validate that required item fields are present
        item_name = cleaned_data.get('item_name', '').strip()
        if item_name:
            if cleaned_data.get('item_min_stock_qty') is None:
                raise forms.ValidationError('Minimum stock quantity is required for creating a new item.')
        
        return cleaned_data
    
    def save(self, commit=True, user=None):
        """Override save to create item if it doesn't exist, generate item_code, and handle branches"""
        instance = super().save(commit=False)
        item_name = self.cleaned_data.get('item_name', '').strip()
        
        # Ensure supplier is set on instance before generating item_code
        supplier = self.cleaned_data.get('supplier')
        if supplier:
            instance.supplier = supplier
        
        # Clear item_code if it's the placeholder value (it will be regenerated)
        if instance.item_code in ['Auto-generated after saving', 'Auto-generated', '']:
            instance.item_code = None
        
        if item_name:
            # Check if item exists, if not create it
            try:
                item = Item.objects.get(name__iexact=item_name, is_active=True)
            except Item.DoesNotExist:
                # Create new Item
                if supplier and supplier.category:
                    category_name = supplier.category.name.upper()
                    category_prefixes = {
                        'PACKAGING': 'PKG',
                        'FOOD': 'FOOD',
                        'BEVERAGE': 'BEV',
                        'EQUIPMENT': 'EQP',
                        'CLEANING SUPPLIES': 'CLN',
                        'OTHER': 'OTH',
                    }
                    prefix = category_prefixes.get(category_name, category_name[:3].upper())
                    
                    # Get the next number for Item item_code - find max number from all existing codes
                    existing_item_codes = Item.objects.filter(
                        item_code__startswith=f'{prefix}-'
                    ).exclude(item_code__isnull=True).exclude(item_code='').values_list('item_code', flat=True)
                    
                    max_number = 0
                    for code in existing_item_codes:
                        try:
                            number = int(code.split('-')[1])
                            if number > max_number:
                                max_number = number
                        except (ValueError, IndexError):
                            continue
                    
                    next_number = max_number + 1
                    item_code = f"{prefix}-{next_number:04d}"
                else:
                    # Fallback if no category
                    item_code = f"ITEM-{Item.objects.count() + 1:04d}"
                
                # Get default brand (first brand) and base_unit from SupplierItem's base_unit
                default_brand = Brand.objects.first()
                if not default_brand:
                    raise ValueError('No brands available. Please create a brand first.')
                
                # Get base_unit from SupplierItem's base_unit field (convert BaseUnit to string)
                base_unit_obj = self.cleaned_data.get('base_unit')
                base_unit_str = 'pcs'  # Default fallback
                if base_unit_obj:
                    # base_unit is a BaseUnit instance, get its name
                    base_unit_str = base_unit_obj.name
                
                # Create the new Item
                # Use the SupplierItem's min_order_qty for the Item's min_order_qty
                supplier_item_min_order_qty = self.cleaned_data.get('min_order_qty', Decimal('0'))
                # Get price_per_unit from SupplierItem form and save to Item
                price_per_unit = self.cleaned_data.get('price_per_unit')
                
                item = Item.objects.create(
                    item_code=item_code,
                    name=item_name,
                    brand=default_brand,
                    base_unit=base_unit_str,
                    min_order_qty=supplier_item_min_order_qty,
                    min_stock_qty=self.cleaned_data.get('item_min_stock_qty', Decimal('0')),
                    price_per_unit=price_per_unit,  # Save price_per_unit to Item
                    is_active=True,
                    created_by=user
                )
            
            instance.item = item
        
        # Generate supplier item code if not already set (only for new items)
        # This should increment based on category prefix, not supplier
        # Always generate for new items (instance.pk is None) and if item_code is not a valid code
        is_new_item = not instance.pk
        current_item_code = instance.item_code or ''
        is_placeholder = current_item_code in ['Auto-generated after saving', 'Auto-generated', '']
        
        if is_new_item and (is_placeholder or not current_item_code) and instance.supplier:
            # Generate code using the supplier's category (not the supplier itself)
            if instance.supplier and instance.supplier.category:
                category_name = instance.supplier.category.name.upper()
                category_prefixes = {
                    'PACKAGING': 'PKG',
                    'FOOD': 'FOOD',
                    'BEVERAGE': 'BEV',
                    'EQUIPMENT': 'EQP',
                    'CLEANING SUPPLIES': 'CLN',
                    'OTHER': 'OTH',
                }
                prefix = category_prefixes.get(category_name, category_name[:3].upper())
                
                # Get all existing SupplierItem codes with this prefix (regardless of supplier)
                # This ensures incrementing works even if the same supplier is used multiple times
                existing_codes = SupplierItem.objects.filter(
                    item_code__startswith=f'{prefix}-'
                ).exclude(item_code__isnull=True).exclude(item_code='').exclude(
                    item_code__icontains='auto-generated'
                ).values_list('item_code', flat=True)
                
                # Find the maximum number from all existing codes with this prefix
                max_number = 0
                for code in existing_codes:
                    try:
                        # Extract number from code (e.g., "PKG-0001" -> 1, "PKG-0023" -> 23)
                        # Code should be in format "PREFIX-NUMBER"
                        parts = code.split('-')
                        if len(parts) == 2 and parts[1].isdigit():
                            number = int(parts[1])
                            if number > max_number:
                                max_number = number
                    except (ValueError, IndexError, AttributeError):
                        # Skip invalid codes (like "Auto-generated after saving")
                        continue
                
                # Generate next number (increment from max)
                next_number = max_number + 1
                generated_code = f"{prefix}-{next_number:04d}"
                
                # Double-check uniqueness and increment if needed (handles race conditions)
                # This ensures the code is truly unique even if multiple items are added simultaneously
                while SupplierItem.objects.filter(item_code=generated_code).exists():
                    next_number += 1
                    generated_code = f"{prefix}-{next_number:04d}"
                
                instance.item_code = generated_code
        
        if commit:
            instance.save()
            # Note: branches are saved to Item, not SupplierItem, so we handle it in the view
        return instance


class PriceDiscussionForm(forms.ModelForm):
    """Form for adding price discussions with suppliers"""
    
    class Meta:
        model = SupplierPriceDiscussion
        fields = ['supplier_item', 'discussed_price', 'discussed_date', 'notes']
        widgets = {
            'supplier_item': forms.HiddenInput(),
            'discussed_price': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Price discussed (OMR)'
            }),
            'discussed_date': forms.DateTimeInput(attrs={
                'class': 'form-input',
                'type': 'datetime-local'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Notes about the price discussion...'
            })
        }
        labels = {
            'discussed_price': 'Discussed Price (OMR)',
            'discussed_date': 'Discussion Date',
            'notes': 'Notes'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['discussed_price'].required = True
        self.fields['discussed_date'].required = True
