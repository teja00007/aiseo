from django.shortcuts import HttpResponse
from api_credits.models import APICredit
from rest_framework import  generics,status
import jwt
from rest_framework_simplejwt.backends import TokenBackend
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.conf import settings

from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import MembershipSerializer,SubscriptionSerializer, UserMembershipSerializer,MembershippaymentSerializer
import datetime
from datetime import timedelta
from datetime import datetime as dt
import json
from rest_framework import generics,status
from rest_framework.response import  Response
import stripe
from django.contrib.auth import get_user_model
User = get_user_model()

today = datetime.date.today()
	

stripe.api_key = settings.STRIPE_SECRET_KEY


class membershipview(generics.GenericAPIView):
	serializer_class = MembershipSerializer
	token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)
	
	@swagger_auto_schema(manual_parameters=[token_param_config])
	def get(self, request):
		queryset = Membership.objects.all()
		serializer = self.serializer_class(queryset,many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)

class usersubscription(generics.GenericAPIView):
	serializer_class = UserMembershipSerializer
	token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)
	
	@swagger_auto_schema(manual_parameters=[token_param_config])
	def get(self, request):
		token = request.GET.get('token')
		try:
			import pdb;pdb.set_trace()
			payload = jwt.decode(token, settings.SECRET_KEY,algorithms='HS256')
			user = User.objects.get(id=payload['user_id'])
			if user.is_verified:
				queryset = UserMembership.objects.filter(user=user)
				serializer = self.serializer_class(queryset,many=True)
				return Response(serializer.data, status=status.HTTP_200_OK)
		except jwt.ExpiredSignatureError as identifier:
			return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
		except jwt.exceptions.DecodeError as identifier:
			return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)	

class usersubscription_expry(generics.GenericAPIView):
	serializer_class = SubscriptionSerializer
	token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)
	
	@swagger_auto_schema(manual_parameters=[token_param_config])
	def get(self, request):
		token = request.GET.get('token')
		try:
			#import pdb;pdb.set_trace()
			payload = jwt.decode(token, settings.SECRET_KEY,algorithms='HS256')
			user = User.objects.get(id=payload['user_id'])
			if user.is_verified:
				user = UserMembership.objects.filter(user=user)[0]
				queryset = Subscription.objects.filter(user_membership=user)[0]
				serializer = self.serializer_class(queryset)
				return Response(serializer.data, status=status.HTTP_200_OK)
		except jwt.ExpiredSignatureError as identifier:
			return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
		except jwt.exceptions.DecodeError as identifier:
			return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)	



class payment_order_create(generics.GenericAPIView):
	serializer_class = MembershippaymentSerializer
	token_param_config = openapi.Parameter(
        'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)
	
	@swagger_auto_schema(manual_parameters=[token_param_config])
	def post(self, request):
		#import pdb;pdb.set_trace()
		token = request.GET.get('token')
		data = self.serializer_class(data=request.data)
		if data:
			data.is_valid()
			plan = data['plan'].value
			# fetch_membership = Membership.objects.filter(membership_type=plan).exists()
			# if fetch_membership == False:
			# 	return redirect('')
			membership = Membership.objects.get(membership_type=plan)

			def init_payment(membership):
				domain = "http://127.0.0.1:8000"
				checkout_session = stripe.checkout.Session.create(
					payment_method_types=['card'],
					line_items=[
						{
							'price_data': {
								'currency': 'usd',
								'unit_amount': int(float(membership.price)*100),
								'product_data': {
									'name': membership.membership_type,
								},
							},
							'quantity': 1,
						},
					],
					metadata={
						"product_id": membership.id
					},
					mode='payment',
					success_url=domain + '/auth/payment/',
					cancel_url=domain + '/cancel/',
				)
				return checkout_session
			payload = jwt.decode(token, settings.SECRET_KEY,algorithms='HS256')
			user = User.objects.get(id=payload['user_id'])
			#email = user.email
			checkout_session = init_payment(membership)
			#print(checkout_session)
			amount = membership.price
			instance = PayHistory.objects.create(amount=amount, payment_for=membership, user=user, paystack_charge_id=checkout_session['id'], paystack_access_code='test')
			if UserMembership.objects.filter(user=instance.user):
				UserMembership.objects.filter(user=instance.user).update(reference_code=checkout_session['id'])
			return Response(checkout_session)


def call_back_url(request):
	#import pdb;pdb.set_trace()
	payload = request.body
	sig_header = request.META['HTTP_STRIPE_SIGNATURE']
	event = None
	try:
		event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
	except ValueError as e:
		# Invalid payload
		return HttpResponse(status=400)
	except stripe.error.SignatureVerificationError as e:
		# Invalid signature
		return HttpResponse(status=400)

	# Handle the checkout.session.completed event
	if event['type'] == 'checkout.session.completed' or event['type'] == "payment_intent.succeeded":
		#import pdb;pdb.set_trace()
		id = json.loads(request.body)['data']['object']['id']
		PayHistory.objects.filter(paystack_charge_id=id).update(paid=True)
		new_payment = PayHistory.objects.get(paystack_charge_id=id)
		instance = Membership.objects.get(id=new_payment.payment_for.id)
		sub = UserMembership.objects.filter(reference_code=id).update(membership=instance)
		user_membership = UserMembership.objects.get(reference_code=id)
		if Subscription.objects.filter(user_membership=user_membership):
			Subscription.objects.filter(user_membership=user_membership).update(expires_in=dt.now().date() + timedelta(days=user_membership.membership.duration))
		else:
			Subscription.objects.create(user_membership=user_membership, expires_in=dt.now().date() + timedelta(days=user_membership.membership.duration))
		#import pdb;pdb.set_trace()
		user = user_membership.user
		plan = user_membership.membership
		MEMBERSHIP_Credits = {
			'Extended': 1000000,
			'Advanced': 100000,
			'Medium': 10000,
			'Basic': 1000
			}
		credit = APICredit.objects.get(user=user)
		APICredit.objects.filter(user=user).update(credits=credit.credits + MEMBERSHIP_Credits[plan.membership_type])
	return HttpResponse(status=200)


# class payment_order_create(generics.GenericAPIView):
# 	serializer_class = MembershippaymentSerializer
# 	token_param_config = openapi.Parameter(
#         'token', in_=openapi.IN_QUERY, description='Description', type=openapi.TYPE_STRING)
	
# 	@swagger_auto_schema(manual_parameters=[token_param_config])
# 	def post(self, request):
# 		#import pdb;pdb.set_trace()
# 		token = request.GET.get('token')
# 		data = self.serializer_class(data=request.data)
# 		if data:
# 			data.is_valid()
# 			plan = data['plan'].value
# 			fetch_membership = Membership.objects.filter(membership_type=plan).exists()
# 			if fetch_membership == False:
# 				return redirect('subscribe')
# 			membership = Membership.objects.get(membership_type=plan)
# 			price = float(membership.price)*100 # We need to multiply the price by 100 because Paystack receives in kobo and not naira.
# 			price = int(price)

# 			def init_payment(price):
# 				keyid = 'rzp_test_o1cnwDwUfD8IEO'
# 				keysecret = 't0va8kvislRlFvRzz4Iwpf8P'
# 				import razorpay
# 				client = razorpay.Client(auth=(keyid, keysecret))

# 				data = { "amount": price, "currency": "INR", "receipt": "order_rcptid_11" }
# 				payment = client.order.create(data=data)
# 				return payment
# 			payload = jwt.decode(token, settings.SECRET_KEY,algorithms='HS256')
# 			user = User.objects.get(id=payload['user_id'])
# 			email = user.email
# 			initialized = init_payment(price)
# 			print(initialized)
# 			amount = price/100
# 			instance = PayHistory.objects.create(amount=amount, payment_for=membership, user=user, paystack_charge_id=initialized['id'], paystack_access_code=initialized['receipt'])
# 			UserMembership.objects.filter(user=instance.user).update(reference_code=initialized['id'])
# 			return Response(initialized)


# def call_back_url(request):
# 	import pdb;pdb.set_trace()
# 	reference = dict(request.POST)
# 	# We need to fetch the reference from PAYMENT
# 	check_pay = PayHistory.objects.filter(paystack_charge_id=reference['razorpay_order_id'][0]).exists()
# 	if check_pay == False:
# 		# This means payment was not made error should be thrown here...
# 		print("Error")
# 	else:
# 		#payment = PayHistory.objects.get(paystack_charge_id=reference['razorpay_order_id'][0])
# 		# We need to fetch this to verify if the payment was successful.
# 		def verify_payment(reference):
# 			keyid = 'rzp_test_o1cnwDwUfD8IEO'
# 			keysecret = 't0va8kvislRlFvRzz4Iwpf8P'
# 			import razorpay
# 			client = razorpay.Client(auth=(keyid, keysecret))
# 			try:
# 				client.utility.verify_subscription_payment_signature({
# 				'razorpay_subscription_id': reference['razorpay_order_id'][0],
# 				'razorpay_payment_id': reference['razorpay_payment_id'][0],
# 				'razorpay_signature': reference['razorpay_signature'][0]
# 				})
# 			except:
# 				pass
# 			return True


# 	initialized = verify_payment(reference)
# 	if initialized:
# 		PayHistory.objects.filter(paystack_charge_id=reference['razorpay_order_id'][0]).update(paid=True)
# 		new_payment = PayHistory.objects.get(paystack_charge_id=reference['razorpay_order_id'][0])
# 		instance = Membership.objects.get(id=new_payment.payment_for.id)
# 		sub = UserMembership.objects.filter(reference_code=reference['razorpay_order_id'][0]).update(membership=instance)
# 		user_membership = UserMembership.objects.get(reference_code=reference['razorpay_order_id'][0])
# 		Subscription.objects.create(user_membership=user_membership, expires_in=dt.now().date() + timedelta(days=user_membership.membership.duration))
# 		return render(request, 'payment_processed.html')
# 	return render(request, 'payment_processed.html')