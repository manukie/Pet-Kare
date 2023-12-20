from rest_framework.views import APIView
from rest_framework.views import Request, Response, status
from rest_framework.pagination import PageNumberPagination
from .serializers import PetSerializer
from .models import Pet
from groups.models import Group
from traits.models import Trait
from django.shortcuts import get_object_or_404


class PetView(APIView, PageNumberPagination):

    def post(self, req: Request) -> Response:
        serializer = PetSerializer(data=req.data)
        serializer.is_valid(raise_exception=True)
        group_data = serializer.validated_data.pop("group")
        traits = serializer.validated_data.pop("traits")

        pet = Pet(**serializer.validated_data)

        try:
            group = Group.objects.get(scientific_name__iexact=group_data["scientific_name"])
        except Group.DoesNotExist:
            group = Group.objects.create(**group_data)

        pet.group = group
        pet.save()

        for trait_data in traits:
            try:
                trait = Trait.objects.get(name__iexact=trait_data["name"])
            except Trait.DoesNotExist:
                trait = Trait.objects.create(**trait_data)
            pet.traits.add(trait)

        serializer = PetSerializer(pet)
        return Response(serializer.data, status.HTTP_201_CREATED)

    def get(self, req: Request) -> Response:
        by_trait = req.query_params.get("trait", None)
        if by_trait:
            pets = Pet.objects.filter(traits__name__iexact=by_trait)
        else:
            pets = Pet.objects.all().order_by("id")
        result = self.paginate_queryset(pets, req)
        serializer = PetSerializer(result, many=True)
        return self.get_paginated_response(serializer.data)


class PetDetailView(APIView):
    def get(self, req: Request, pet_id: int) -> Response:

        found_pet = get_object_or_404(Pet, pk=pet_id)
        serializer = PetSerializer(found_pet)
        return Response(serializer.data)

    def delete(self, req: Request, pet_id: int) -> Response:
        found_pet = get_object_or_404(Pet, pk=pet_id)
        found_pet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request: Request, pet_id: int) -> Response:
        try:
            pet = Pet.objects.get(id=pet_id)
        except Pet.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        pet.name = request.data.get('name', pet.name)
        pet.age = request.data.get('age', pet.age)
        pet.weight = request.data.get('weight', pet.weight)
        valid_sex_values = ['male', 'female', 'not informed']
        pet_sex = request.data.get('sex', pet.sex)
        if pet_sex.lower() not in valid_sex_values:
            return Response({"sex": ['"{}" is not a valid choice.'.format(pet_sex)]}, status=status.HTTP_400_BAD_REQUEST)
        pet.sex = pet_sex

        group_data = request.data.get('group', {})
        group, _ = Group.objects.get_or_create(**group_data)
        pet.group = group

        pet.traits.set([])

        traits_data = request.data.get('traits', [])
        for trait_data in traits_data:
            trait, _ = Trait.objects.get_or_create(name__iexact=trait_data['trait_name'])
            pet.traits.add(trait)

        pet.save()

        serializer = PetSerializer(pet)
        return Response(serializer.data, status=status.HTTP_200_OK)
