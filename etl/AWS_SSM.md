# Use AWS SSM from Lambda

- https://www.youtube.com/watch?v=90AqkOmhVhc&t=124s

## Store a new secret

<img width="1158" alt="image" src="https://github.com/user-attachments/assets/4be8f4e6-a842-4858-b032-ac8ce25b20e0">

<img width="1158" alt="image" src="https://github.com/user-attachments/assets/8bbc1d7c-e24b-45f3-a764-05414012d5a2">

<img width="1158" alt="image" src="https://github.com/user-attachments/assets/991cb5a4-38ea-45e7-8001-6a0e48c889c6">

## Copy code

<img width="1158" alt="image" src="https://github.com/user-attachments/assets/40b1b798-f5cd-4154-881a-d23e3e06ddda">

## Add these two lines on at the end of the function

```python
result = json.loads(secret)
return result[secret_name]
```

## Edit role

<img width="1158" alt="image" src="https://github.com/user-attachments/assets/ff9ccf16-c26d-473e-a0b7-e1f73951b067">

## Add permissions -> Attach policies

<img width="1158" alt="image" src="https://github.com/user-attachments/assets/00e1cff9-fb18-4439-9ec9-e62764e469c7">

## Add permission policy SecretsManagerReadWrite

<img width="1158" alt="image" src="https://github.com/user-attachments/assets/6ceb04a7-85cd-4a3f-945e-3a2281920d10">

## Paste code into lambda function
