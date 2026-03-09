from django import forms
from .models import Product, Category


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name',
            'description',
            'price',
            'category',
            'phone',
            'city',
            'image',
            'is_wholesale',
            'bulk_price',
            'minimum_quantity',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        is_wholesale = cleaned_data.get('is_wholesale')
        bulk_price = cleaned_data.get('bulk_price')
        minimum_quantity = cleaned_data.get('minimum_quantity')

        if is_wholesale:
            if not bulk_price:
                self.add_error('bulk_price', 'Bulk price is required for wholesale listings.')
            if not minimum_quantity:
                self.add_error('minimum_quantity', 'Minimum quantity is required for wholesale listings.')

        return cleaned_data


class ReviewForm(forms.Form):
    rating = forms.ChoiceField(choices=[(i, f'{i} ★') for i in range(1, 6)], label='Rating')
    comment = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, label='Comment')