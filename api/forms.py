from django import forms
from api.models import ProductReview

class ProductReviewForm(forms.ModelForm):
    review = forms.CharField(
        widget=forms.Textarea(attrs={'placeholder': 'Write a review'})
        )
    
    class Meta:
        model = ProductReview
        fields = ['review', 'rating']